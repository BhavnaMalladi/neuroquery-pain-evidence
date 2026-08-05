"""Build the results notebook from the precomputed tables and figures.

Run this after the analysis scripts have produced their outputs. It assembles a notebook that loads
each result table and shows the matching figure, so a reader can open it and see everything without
rerunning anything.
"""
import os
import nbformat as nbf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def md(text):
    return nbf.v4.new_markdown_cell(text)


def code(text):
    return nbf.v4.new_code_cell(text)


HEADER = code(
    "import os, json\n"
    "import pandas as pd\n"
    "from IPython.display import Image, display\n"
    "DATA, FIG = 'data', 'figures'\n"
    "def show(csv=None, png=None):\n"
    "    if csv and os.path.exists(os.path.join(DATA, csv)):\n"
    "        display(pd.read_csv(os.path.join(DATA, csv)))\n"
    "    if png and os.path.exists(os.path.join(FIG, png)):\n"
    "        display(Image(os.path.join(FIG, png)))\n"
)


def main():
    nb = nbf.v4.new_notebook()
    cells = [
        md("# Representation bias in the NeuroQuery pain corpus\n\n"
           "This notebook reads the precomputed tables in `data/` and shows each result. To rebuild "
           "the tables, run the scripts in `src/` as listed in the README."),
        HEADER,
        md("## A. Size-fair reporting audit\n\n"
           "Fraction of pain studies reporting a peak near each region, with a sphere of the same "
           "radius at every region. The ratio of the cortical mean to the subcortical mean is "
           "reported across radii, with a threshold sweep to show the selection does not drive it."),
        code("show('ratio_by_radius.csv', 'reporting_forest.png')\nshow('threshold_sweep.csv', 'ratio_by_radius.png')"),
        md("## B. Region sampling of the predictive map\n\n"
           "NeuroQuery's encoding map for the single query 'pain', read at the region coordinates. "
           "This is a predictive encoding value, reported on its own terms."),
        code("show('roi_zvalues.csv', 'roi_zvalues.png')"),
        md("## C. Mention frequency versus reporting frequency\n\n"
           "For the same pain studies, how often each region is named in the text versus how often a "
           "coordinate is reported for it. A gap isolates coordinate reporting from discussion."),
        code("show('mention_vs_reporting.csv', 'mention_vs_reporting.png')"),
        md("## D. Change across publication year\n\n"
           "The cortical to subcortical reporting ratio by year, with a weighted trend. A falling "
           "ratio points to a measurement limit, a flat ratio to a reporting habit."),
        code("show('year_trend.csv', 'year_trend.png')"),
        md("## E. Semantic anchoring\n\n"
           "How strongly 'pain' co-occurs with cortical versus subcortical region terms across the "
           "corpus, computed from raw counts with no model involved."),
        code("show('semantic_anchoring.csv', 'semantic_anchoring.png')\nshow('pain_nearest_terms.csv')"),
        md("## Summary across measures"),
        code("show(png='convergence_summary.png')"),
    ]
    nb["cells"] = cells
    out = os.path.join(ROOT, "neuroquery_evidence.ipynb")
    with open(out, "w") as f:
        nbf.write(nb, f)
    print("wrote", out)


if __name__ == "__main__":
    main()
