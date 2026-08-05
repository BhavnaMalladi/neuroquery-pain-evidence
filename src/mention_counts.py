"""Idea C. Mention frequency versus reporting frequency.

For the same pain studies used in the reporting audit, count how often each region is named in
the text at all, using raw word counts across title, abstract, body and keywords. Compare that
mention rate to the reporting rate from Idea A. If a region is mentioned about as often as another
but has its coordinates reported far less, the gap is specific to coordinate reporting rather than
to whether the field discusses the region.

Synonym sets are intersected with the NeuroQuery vocabulary, so only terms that actually exist in
the data are counted, and the terms used per region are logged. A leave one synonym out pass checks
that no single term drives a region's mention rate.

Run audit_reporting.py first.

Writes:
  data/mention_vs_reporting.csv, data/mention_synonyms_used.json
  figures/mention_vs_reporting.png
"""
import os
import json
import numpy as np
import pandas as pd
from scipy import sparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "nq_cache")
DATA = os.path.join(ROOT, "data")
FIG = os.path.join(ROOT, "figures")

CORTICAL = "#b2182b"
SUBCORT = "#2166ac"

# region: (class, [reporting ROI names to average], [candidate synonym terms])
REGIONS = {
    "ACC": ("cortical", ["dACC"],
            ["anterior cingulate", "anterior cingulate cortex", "anterior cingulate gyrus",
             "anterior cingulate area", "caudal anterior cingulate cortex", "cingulate anterior"]),
    "anterior insula": ("cortical", ["aInsula_L", "aInsula_R"],
            ["anterior insula", "anterior insular", "anterior insular cortex",
             "agranular insular cortex", "insula anterior"]),
    "S1": ("cortical", ["S1"],
            ["primary somatosensory", "primary somatosensory cortex", "primary somatosensory area",
             "postcentral gyrus", "postcentral"]),
    "S2": ("cortical", ["S2"],
            ["secondary somatosensory", "secondary somatosensory cortex",
             "secondary somatosensory area", "parietal operculum"]),
    "posterior insula": ("cortical", ["pInsula_L", "pInsula_R"],
            ["posterior insula", "posterior insular cortex"]),
    "aMCC": ("cortical", ["aMCC"],
            ["midcingulate", "midcingulate cortex", "anterior midcingulate cortex"]),
    "Thalamus": ("subcortical", ["Thalamus"],
            ["thalamus", "thalamic", "dorsal thalamus", "medial thalamus", "posterior thalamus"]),
    "PAG": ("subcortical", ["PAG"],
            ["periaqueductal", "periaqueductal gray", "periaqueductal gray matter",
             "periaqueductal grey", "central gray"]),
    "Parabrachial": ("subcortical", ["Parabrachial"],
            ["parabrachial", "parabrachial nucleus", "lateral parabrachial nucleus"]),
    "Hypothalamus": ("subcortical", ["Hypothalamus"],
            ["hypothalamus", "hypothalamic", "lateral hypothalamus", "lateral hypothalamic area",
             "medial hypothalamus", "anterior hypothalamus"]),
    "Amygdala": ("subcortical", ["Amygdala"],
            ["amygdala", "amygdalar", "amygdaloid", "amygdala central", "amygdala basolateral"]),
    "RVM": ("subcortical", ["RVM"],
            ["nucleus raphe magnus", "raphe magnus"]),
    "NAc": ("subcortical", ["NAc_L", "NAc_R"],
            ["nucleus accumbens", "accumbens", "ventral striatum", "striatum ventral"]),
}


def load_counts():
    vocab = [w.strip() for w in open(os.path.join(CACHE, "vocab_7547.txt"), encoding="utf-8")]
    idx = {w: i for i, w in enumerate(vocab)}
    total = None
    for name in ["counts_abstract_7547.npz", "counts_body_7547.npz",
                 "counts_keywords_7547.npz", "counts_title_7547.npz"]:
        m = sparse.load_npz(os.path.join(CACHE, name))
        if m.shape[0] == len(vocab):   # stored as terms by docs, put docs first
            m = m.T
        total = m if total is None else total + m
    return vocab, idx, total.tocsc()


def mention_mask(counts, cols):
    if not cols:
        return None
    sub = counts[:, cols].sum(axis=1)
    return np.asarray(sub).ravel() > 0


def main():
    meta = pd.read_csv(os.path.join(CACHE, "metadata.tsv.gz"), sep="\t")
    vocab, idx, counts = load_counts()
    if counts.shape[0] != len(meta):
        raise SystemExit("count row mismatch %d vs %d" % (counts.shape[0], len(meta)))

    pain = pd.read_csv(os.path.join(DATA, "neuroquery_pain_studies.csv")).pmid.astype(int)
    rows = np.where(meta["id"].astype(np.int64).isin(set(pain)).to_numpy())[0]
    n = len(rows)
    print("pain studies for mention counting:", n)

    report = pd.read_csv(os.path.join(DATA, "reporting_audit_extended.csv"))
    report6 = report[report.R_mm == 6].set_index("roi")["rate"].to_dict()

    used = {}
    out = []
    for region, (kind, roi_names, syns) in REGIONS.items():
        cols = [idx[s] for s in syns if s in idx]
        used[region] = [s for s in syns if s in idx]
        mask = mention_mask(counts, cols)
        mention_rate = float(mask[rows].mean()) if mask is not None else 0.0
        report_rate = float(np.mean([report6[r] for r in roi_names if r in report6]))
        out.append({"region": region, "kind": kind, "n_synonyms_used": len(cols),
                    "mention_rate": mention_rate, "report_rate": report_rate,
                    "mention_minus_report": mention_rate - report_rate})
    res = pd.DataFrame(out).sort_values(["kind", "mention_rate"], ascending=[True, False])
    res.to_csv(os.path.join(DATA, "mention_vs_reporting.csv"), index=False)
    with open(os.path.join(DATA, "mention_synonyms_used.json"), "w") as f:
        json.dump(used, f, indent=2)
    print("\n", res.to_string(index=False))

    cort = res[res.kind == "cortical"]
    sub = res[res.kind == "subcortical"]
    mention_ratio = cort.mention_rate.mean() / sub.mention_rate.mean()
    report_ratio = cort.report_rate.mean() / sub.report_rate.mean()
    print("\ncortical:subcortical mention ratio  %.2f" % mention_ratio)
    print("cortical:subcortical reporting ratio %.2f" % report_ratio)

    # leave one synonym out sensitivity on the cortical:subcortical mention ratio
    sens = []
    for region, (kind, roi_names, syns) in REGIONS.items():
        present = [s for s in syns if s in idx]
        if len(present) < 2:
            continue
        for drop in present:
            cols = [idx[s] for s in present if s != drop]
            mask = mention_mask(counts, cols)
            mr = float(mask[rows].mean())
            sens.append({"region": region, "dropped": drop, "mention_rate": mr})
    pd.DataFrame(sens).to_csv(os.path.join(DATA, "mention_leave_one_out.csv"), index=False)

    order = res.sort_values("mention_rate")
    y = np.arange(len(order))
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(y - 0.2, order.mention_rate, height=0.4, color="#6a6a6a", label="mentioned in text")
    cols = [CORTICAL if k == "cortical" else SUBCORT for k in order.kind]
    ax.barh(y + 0.2, order.report_rate, height=0.4, color=cols, label="coordinate reported")
    ax.set_yticks(y)
    ax.set_yticklabels(order.region)
    ax.set_xlabel("fraction of pain studies")
    ax.set_title("Mentioned in text versus coordinate reported\n"
                 "mention ratio %.2f, reporting ratio %.2f (cortical over subcortical)"
                 % (mention_ratio, report_ratio))
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "mention_vs_reporting.png"), dpi=200)
    plt.close(fig)

    prov = {"analysis": "C mention vs reporting", "n_pain_studies": n,
            "mention_ratio": mention_ratio, "reporting_ratio": report_ratio}
    with open(os.path.join(DATA, "provenance_C.json"), "w") as f:
        json.dump(prov, f, indent=2)
    print("done")


if __name__ == "__main__":
    main()
