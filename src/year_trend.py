"""Idea D. Does the reporting imbalance change across publication year.

NeuroQuery ships study titles and PubMed identifiers but not publication years, so the year is
recovered from PubMed for the pain study subset only. The cortical to subcortical reporting ratio
is then computed within each year and tested for a trend. A falling ratio would point to a
measurement limit that improving hardware relaxes; a flat ratio would point to a reporting habit
that persists regardless of hardware.

Run audit_reporting.py first so the pain study list exists.

Writes:
  data/pain_study_years.csv, data/year_trend.csv
  figures/year_trend.png
"""
import os
import json
import time
import urllib.request
import urllib.parse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import rois
from audit_reporting import coords_by_study, audit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "nq_cache")
DATA = os.path.join(ROOT, "data")
FIG = os.path.join(ROOT, "figures")

ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
EMAIL = os.environ.get("NCBI_EMAIL", "")
ERA_CUTOFF = 2016


def fetch_years(pmids, batch=200):
    years = {}
    for start in range(0, len(pmids), batch):
        chunk = pmids[start:start + batch]
        params = {"db": "pubmed", "id": ",".join(str(p) for p in chunk),
                  "retmode": "json", "tool": "neuroquery-pain-evidence"}
        if EMAIL:
            params["email"] = EMAIL
        url = ESUMMARY + "?" + urllib.parse.urlencode(params)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url, timeout=60) as r:
                    payload = json.load(r)
                break
            except Exception as e:
                if attempt == 3:
                    raise
                time.sleep(2 * (attempt + 1))
        res = payload.get("result", {})
        for pmid in res.get("uids", []):
            rec = res.get(pmid, {})
            date = rec.get("pubdate") or rec.get("epubdate") or ""
            y = date[:4]
            if y.isdigit():
                years[int(pmid)] = int(y)
        time.sleep(0.34)
        print("  years fetched: %d / %d" % (len(years), len(pmids)))
    return years


def load_or_fetch_years(pmids):
    path = os.path.join(DATA, "pain_study_years.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        have = set(df.pmid)
        missing = [p for p in pmids if p not in have]
        if not missing:
            return df
        extra = fetch_years(missing)
        df = pd.concat([df, pd.DataFrame({"pmid": list(extra), "year": list(extra.values())})],
                       ignore_index=True)
    else:
        y = fetch_years(pmids)
        df = pd.DataFrame({"pmid": list(y), "year": list(y.values())})
    df = df.drop_duplicates("pmid").sort_values("pmid")
    df.to_csv(path, index=False)
    return df


def main():
    pmids = pd.read_csv(os.path.join(DATA, "neuroquery_pain_studies.csv")).pmid.astype(int).tolist()
    years = load_or_fetch_years(pmids)
    print("year range %d to %d, n=%d" % (years.year.min(), years.year.max(), len(years)))
    print(years.year.value_counts().sort_index().to_string())

    coords = pd.read_csv(os.path.join(CACHE, "coordinates.tsv.gz"), sep="\t")
    ymap = dict(zip(years.pmid, years.year))

    rows = []
    for y, g in years.groupby("year"):
        sp = coords_by_study(coords, g.pmid.tolist())
        if len(sp) < 5:
            continue
        a = audit(rois.core(), sp, [6])
        cort = a[a.kind == "cortical"].rate.mean()
        sub = a[a.kind == "subcortical"].rate.mean()
        rows.append({"year": int(y), "n": len(sp), "cortical_mean": cort,
                     "subcortical_mean": sub, "ratio": cort / sub if sub else np.nan})
    trend = pd.DataFrame(rows).dropna()
    trend.to_csv(os.path.join(DATA, "year_trend.csv"), index=False)
    print("\nper year ratio:")
    print(trend.to_string(index=False))

    # weighted least squares of ratio on year, weight by study count
    import statsmodels.api as sm
    X = sm.add_constant(trend.year.to_numpy(dtype=float))
    wls = sm.WLS(trend.ratio.to_numpy(), X, weights=trend.n.to_numpy(dtype=float)).fit()
    slope = wls.params[1]
    slope_p = wls.pvalues[1]
    print("\nWLS slope on year: %.4f per year, p=%.3f" % (slope, slope_p))

    early = trend[trend.year < ERA_CUTOFF]
    late = trend[trend.year >= ERA_CUTOFF]

    def wmean(d):
        return np.average(d.ratio, weights=d.n) if len(d) else np.nan
    print("era means: before %d = %.2f (studies %d), from %d = %.2f (studies %d)"
          % (ERA_CUTOFF, wmean(early), int(early.n.sum()), ERA_CUTOFF, wmean(late), int(late.n.sum())))

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(trend.year, trend.ratio, s=trend.n * 1.2, color="#4d4d4d", alpha=0.7,
               edgecolor="k", linewidth=0.3, label="year (point size = studies)")
    xs = np.array([trend.year.min(), trend.year.max()], dtype=float)
    ax.plot(xs, wls.params[0] + slope * xs, color="#b2182b", lw=1.6,
            label="WLS trend (slope %.3f/yr, p=%.2f)" % (slope, slope_p))
    ax.axhline(1.0, color="k", lw=0.8, ls=":")
    ax.set_xlabel("publication year")
    ax.set_ylabel("cortical to subcortical reporting ratio (R = 6 mm)")
    ax.set_title("Reporting imbalance across publication year")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "year_trend.png"), dpi=200)
    plt.close(fig)

    prov = {"analysis": "D year trend", "n_studies_with_year": len(years),
            "year_min": int(years.year.min()), "year_max": int(years.year.max()),
            "wls_slope_per_year": float(slope), "wls_slope_p": float(slope_p),
            "era_cutoff": ERA_CUTOFF}
    with open(os.path.join(DATA, "provenance_D.json"), "w") as f:
        json.dump(prov, f, indent=2)
    print("done")


if __name__ == "__main__":
    main()
