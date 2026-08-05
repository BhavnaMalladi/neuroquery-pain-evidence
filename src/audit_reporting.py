"""Idea A. Size fair reporting audit on the NeuroQuery coordinate database.

Select pain studies from NeuroQuery's own combined text tf-idf, then measure how often each
a priori region is reported across those studies with a sphere of fixed radius. Because the
radius is identical for every region, the reporting rate does not reward a region for being
large.

Primary study selection matches the pain study fraction to a fixed target, so the threshold is
set by a rule rather than by hand, and a sweep across thresholds shows the result does not hinge
on that choice.

Writes:
  data/neuroquery_pain_studies.csv
  data/reporting_audit_core.csv, data/reporting_audit_extended.csv
  data/ratio_by_radius.csv, data/threshold_sweep.csv
  figures/reporting_forest.png, figures/ratio_by_radius.png
"""
import os
import json
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import mannwhitneyu
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import rois

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "nq_cache")
DATA = os.path.join(ROOT, "data")
FIG = os.path.join(ROOT, "figures")
for d in (DATA, FIG):
    os.makedirs(d, exist_ok=True)

RADII = [6, 8, 10, 12]
TARGET_FRACTION = 0.036   # pain study fraction to match when picking the primary threshold
SWEEP = [0.0005, 0.001, 0.002, 0.003, 0.005]
CORTICAL = "#b2182b"
SUBCORT = "#2166ac"


def load_corpus():
    meta = pd.read_csv(os.path.join(CACHE, "metadata.tsv.gz"), sep="\t")
    vocab = [w.strip() for w in open(os.path.join(CACHE, "vocab_6308.txt"), encoding="utf-8")]
    tfidf = sparse.load_npz(os.path.join(CACHE, "tfidf_6308.npz"))
    if tfidf.shape[0] == len(vocab) and tfidf.shape[1] == len(meta):
        tfidf = tfidf.T
    tfidf = tfidf.tocsc()
    if tfidf.shape[0] != len(meta) or tfidf.shape[1] != len(vocab):
        raise SystemExit("tfidf shape %s does not match meta %d and vocab %d"
                         % (tfidf.shape, len(meta), len(vocab)))
    coords = pd.read_csv(os.path.join(CACHE, "coordinates.tsv.gz"), sep="\t")
    return meta, vocab, tfidf, coords


def pain_column(vocab, tfidf):
    idx = vocab.index("pain")
    col = np.asarray(tfidf[:, idx].todense()).ravel()
    return col


def select_pmids(meta, pain, threshold):
    mask = pain > threshold
    return meta.loc[mask, "id"].astype(np.int64).to_numpy()


def threshold_for_fraction(pain, fraction):
    nonzero = np.sort(pain[pain > 0])
    if len(nonzero) == 0:
        return 0.0
    keep = int(round(fraction * len(pain)))
    keep = min(max(keep, 1), len(nonzero))
    return float(nonzero[-keep])


def coords_by_study(coords, pmids):
    keep = coords[coords["id"].isin(set(int(p) for p in pmids))]
    out = {}
    for sid, g in keep.groupby("id"):
        out[int(sid)] = g[["x", "y", "z"]].to_numpy(dtype=float)
    return out


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def audit(roi_dict, study_pts, radii):
    rows = []
    studies = list(study_pts.values())
    n = len(studies)
    for name, (x, y, z, kind) in roi_dict.items():
        c = np.array([x, y, z], dtype=float)
        for R in radii:
            k = 0
            for pts in studies:
                if len(pts) and np.min(np.linalg.norm(pts - c, axis=1)) <= R:
                    k += 1
            lo, hi = wilson(k, n)
            rows.append({"roi": name, "kind": kind, "R_mm": R, "k": k, "n": n,
                         "rate": k / n if n else 0.0, "lo": lo, "hi": hi})
    return pd.DataFrame(rows)


def summarise(audit_df):
    rows = []
    for R, g in audit_df.groupby("R_mm"):
        cort = g[g.kind == "cortical"].rate
        sub = g[g.kind == "subcortical"].rate
        u, p = mannwhitneyu(cort, sub, alternative="greater")
        rows.append({"R_mm": R, "cortical_mean": cort.mean(), "subcortical_mean": sub.mean(),
                     "ratio": cort.mean() / sub.mean() if sub.mean() else np.nan,
                     "mannwhitney_p": p, "n_studies": int(g.n.iloc[0])})
    return pd.DataFrame(rows)


def forest_figure(audit_df, path, title):
    d = audit_df[audit_df.R_mm == 6].copy()
    d = d.sort_values("rate")
    y = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(7.5, 6))
    for i, (_, r) in enumerate(d.iterrows()):
        col = CORTICAL if r.kind == "cortical" else SUBCORT
        marker = "o" if r.kind == "cortical" else "^"
        ax.plot([r.lo, r.hi], [i, i], color=col, lw=1.4, zorder=1)
        ax.scatter([r.rate], [i], color=col, marker=marker, s=55, zorder=2, edgecolor="k", linewidth=0.4)
    ax.set_yticks(y)
    ax.set_yticklabels(d.roi)
    cort_mean = d[d.kind == "cortical"].rate.mean()
    sub_mean = d[d.kind == "subcortical"].rate.mean()
    ax.axvline(cort_mean, color=CORTICAL, ls="--", lw=1, label="cortical mean")
    ax.axvline(sub_mean, color=SUBCORT, ls=":", lw=1, label="subcortical mean")
    ax.set_xlabel("fraction of pain studies reporting a peak within 6 mm (Wilson 95% CI)")
    ax.set_title(title)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def ratio_figure(core_sum, ext_sum, path):
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.plot(core_sum.R_mm, core_sum.ratio, "-o", color="#333333", label="core 10 regions")
    ax.plot(ext_sum.R_mm, ext_sum.ratio, "-s", color="#888888", label="extended 16 regions")
    ax.axhline(1.0, color="k", lw=0.8, ls=":")
    for _, r in core_sum.iterrows():
        ax.annotate("%.2f" % r.ratio, (r.R_mm, r.ratio), textcoords="offset points",
                    xytext=(0, 7), ha="center", fontsize=8)
    ax.set_xlabel("sphere radius (mm)")
    ax.set_ylabel("cortical to subcortical reporting ratio")
    ax.set_title("Cortical over subcortical reporting, by sphere radius")
    ax.set_ylim(bottom=0.8)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main():
    meta, vocab, tfidf, coords = load_corpus()
    pain = pain_column(vocab, tfidf)
    thr = threshold_for_fraction(pain, TARGET_FRACTION)
    pmids = select_pmids(meta, pain, thr)
    print("primary threshold %.5f selects %d pain studies (%.2f%% of corpus)"
          % (thr, len(pmids), 100 * len(pmids) / len(meta)))

    study_pts = coords_by_study(coords, pmids)
    print("pain studies with coordinates: %d" % len(study_pts))
    pd.DataFrame({"pmid": sorted(study_pts.keys())}).to_csv(
        os.path.join(DATA, "neuroquery_pain_studies.csv"), index=False)

    core_audit = audit(rois.core(), study_pts, RADII)
    ext_audit = audit(rois.extended(), study_pts, RADII)
    core_audit.to_csv(os.path.join(DATA, "reporting_audit_core.csv"), index=False)
    ext_audit.to_csv(os.path.join(DATA, "reporting_audit_extended.csv"), index=False)

    core_sum = summarise(core_audit)
    ext_sum = summarise(ext_audit)
    core_sum["roi_set"] = "core10"
    ext_sum["roi_set"] = "extended16"
    ratio_tab = pd.concat([core_sum, ext_sum], ignore_index=True)
    ratio_tab.to_csv(os.path.join(DATA, "ratio_by_radius.csv"), index=False)
    print("\ncore 10 by radius:")
    print(core_sum.to_string(index=False))

    sweep_rows = []
    for t in SWEEP:
        ids = select_pmids(meta, pain, t)
        sp = coords_by_study(coords, ids)
        a = audit(rois.core(), sp, [6])
        cort = a[a.kind == "cortical"].rate.mean()
        sub = a[a.kind == "subcortical"].rate.mean()
        sweep_rows.append({"threshold": t, "n_studies": len(sp),
                           "cortical_mean": cort, "subcortical_mean": sub,
                           "ratio": cort / sub if sub else np.nan})
    sweep = pd.DataFrame(sweep_rows)
    sweep.to_csv(os.path.join(DATA, "threshold_sweep.csv"), index=False)
    print("\nthreshold sweep (core 10, R=6):")
    print(sweep.to_string(index=False))

    forest_figure(core_audit, os.path.join(FIG, "reporting_forest.png"),
                  "NeuroQuery pain reporting, core 10 regions (n=%d studies)" % len(study_pts))
    ratio_figure(core_sum, ext_sum, os.path.join(FIG, "ratio_by_radius.png"))

    prov = {"analysis": "A reporting audit", "primary_threshold": thr,
            "target_fraction": TARGET_FRACTION, "n_pain_studies": len(study_pts),
            "radii_mm": RADII, "roi_core": rois.core(), "roi_extended": rois.extended()}
    with open(os.path.join(DATA, "provenance_A.json"), "w") as f:
        json.dump(prov, f, indent=2, default=list)
    print("\ndone")


if __name__ == "__main__":
    main()
