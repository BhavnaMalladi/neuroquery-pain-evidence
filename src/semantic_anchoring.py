"""Idea E. Semantic anchoring of pain in the field's own vocabulary.

Using the raw word counts, measure how strongly the term "pain" co-occurs with cortical region
terms versus subcortical region terms across the whole corpus. This is a co-occurrence structure
computed directly from the data, with no trained model involved. If "pain" sits closer to cortical
terms, the field's vocabulary itself anchors pain to cortex.

A short validation checks that the same measure recovers obviously pain related terms as the closest
neighbors of "pain", so the metric is behaving sensibly before it is used on the region terms.

Writes:
  data/semantic_anchoring.csv, data/pain_nearest_terms.csv
  figures/semantic_anchoring.png
"""
import os
import json
import numpy as np
import pandas as pd
from scipy import sparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from mention_counts import REGIONS, load_counts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
FIG = os.path.join(ROOT, "figures")

CORTICAL = "#b2182b"
SUBCORT = "#2166ac"


def occurrence_matrix(counts):
    binary = (counts > 0).astype(np.float32).tocsc()
    norms = np.sqrt(np.asarray(binary.multiply(binary).sum(axis=0)).ravel())
    norms[norms == 0] = 1.0
    return binary, norms


def cosine_to(term_idx, binary, norms):
    v = binary[:, term_idx]
    dots = np.asarray((binary.T @ v).todense()).ravel()
    return dots / (norms * norms[term_idx])


def main():
    vocab, idx, counts = load_counts()
    binary, norms = occurrence_matrix(counts)
    if "pain" not in idx:
        raise SystemExit("no pain term in vocabulary")
    sims = cosine_to(idx["pain"], binary, norms)

    order = np.argsort(sims)[::-1]
    near = [(vocab[i], float(sims[i])) for i in order if vocab[i] != "pain"][:25]
    pd.DataFrame(near, columns=["term", "cosine_to_pain"]).to_csv(
        os.path.join(DATA, "pain_nearest_terms.csv"), index=False)
    print("nearest terms to 'pain' (validation):")
    for t, s in near[:12]:
        print("  %.3f  %s" % (s, t))

    rows = []
    for region, (kind, roi_names, syns) in REGIONS.items():
        present = [s for s in syns if s in idx]
        if not present:
            continue
        vals = [sims[idx[s]] for s in present]
        rows.append({"region": region, "kind": kind,
                     "anchoring_mean": float(np.mean(vals)),
                     "anchoring_max": float(np.max(vals)),
                     "n_terms": len(present)})
    res = pd.DataFrame(rows).sort_values(["kind", "anchoring_mean"], ascending=[True, False])
    res.to_csv(os.path.join(DATA, "semantic_anchoring.csv"), index=False)
    print("\n", res.to_string(index=False))

    cort = res[res.kind == "cortical"].anchoring_mean.mean()
    sub = res[res.kind == "subcortical"].anchoring_mean.mean()
    print("\nmean pain anchoring: cortical %.4f, subcortical %.4f, ratio %.2f"
          % (cort, sub, cort / sub if sub else np.nan))

    order2 = res.sort_values("anchoring_mean")
    y = np.arange(len(order2))
    cols = [CORTICAL if k == "cortical" else SUBCORT for k in order2.kind]
    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.barh(y, order2.anchoring_mean, color=cols, edgecolor="k", linewidth=0.4)
    ax.axvline(cort, color=CORTICAL, ls="--", lw=1, label="cortical mean")
    ax.axvline(sub, color=SUBCORT, ls=":", lw=1, label="subcortical mean")
    ax.set_yticks(y)
    ax.set_yticklabels(order2.region)
    ax.set_xlabel("co-occurrence with 'pain' across the corpus (cosine)")
    ax.set_title("How closely each region term co-occurs with 'pain'")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "semantic_anchoring.png"), dpi=200)
    plt.close(fig)

    prov = {"analysis": "E semantic anchoring", "cortical_mean": cort, "subcortical_mean": sub,
            "ratio": cort / sub if sub else None}
    with open(os.path.join(DATA, "provenance_E.json"), "w") as f:
        json.dump(prov, f, indent=2)
    print("done")


if __name__ == "__main__":
    main()
