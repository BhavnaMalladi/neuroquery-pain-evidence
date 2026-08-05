"""Summary figure across analyses.

Collects the cortical over subcortical contrast from each analysis that has run and puts them side
by side, so it is easy to see whether independent measures point the same way. Reads whatever result
files are present, so it works before Idea B has been run.

Writes:
  figures/convergence_summary.png
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
FIG = os.path.join(ROOT, "figures")


def load_json(name):
    path = os.path.join(DATA, name)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def main():
    # Ordered as a gradient: how the field talks about regions on the left, how it
    # reports their coordinates on the right. Idea B uses a signed encoding statistic,
    # so it is shown as its own per-region figure rather than as a ratio here.
    bars = []

    e = load_json("provenance_E.json")
    if e and e.get("ratio"):
        bars.append(("co-occurrence\nwith 'pain'", e["ratio"]))

    c = load_json("provenance_C.json")
    if c:
        bars.append(("mentioned\nin text", c["mention_ratio"]))
        bars.append(("coordinate reported\n(region groups)", c["reporting_ratio"]))

    ratio_tab = os.path.join(DATA, "ratio_by_radius.csv")
    if os.path.exists(ratio_tab):
        df = pd.read_csv(ratio_tab)
        r6 = df[(df.roi_set == "core10") & (df.R_mm == 6)]
        if len(r6):
            bars.append(("coordinate reported\n(core 10, 6 mm)", float(r6.ratio.iloc[0])))

    if not bars:
        print("no result files yet; run the analyses first")
        return

    labels = [b[0] for b in bars]
    vals = [b[1] for b in bars]
    x = np.arange(len(bars))
    shades = plt.cm.Greys(np.linspace(0.40, 0.85, len(bars)))
    fig, ax = plt.subplots(figsize=(1.7 * len(bars) + 2, 4.8))
    ax.bar(x, vals, color=shades, edgecolor="k", linewidth=0.4, width=0.62)
    ax.axhline(1.0, color="#b2182b", lw=1, ls="--", label="equal (no imbalance)")
    for xi, v in zip(x, vals):
        ax.annotate("%.2f" % v, (xi, v), textcoords="offset points", xytext=(0, 4),
                    ha="center", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("cortical over subcortical")
    ax.set_title("The imbalance grows from how pain is discussed to how it is reported")
    ax.set_xlabel("how the field talks about regions  (left)  to  how it reports their coordinates  (right)",
                  fontsize=8.5, color="#555555")
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "convergence_summary.png"), dpi=200)
    plt.close(fig)
    print("wrote convergence_summary.png with", len(bars), "measures")


if __name__ == "__main__":
    main()
