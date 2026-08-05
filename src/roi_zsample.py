"""Idea B. Read the NeuroQuery encoding map for "pain" at the region coordinates.

This is the one analysis that uses the trained NeuroQuery model. It is held to a single reference
term, "pain", sampled at the same fixed coordinates as the reporting audit, so the known problems of
free text and combined queries do not enter. The value returned is NeuroQuery's rescaled prediction
z, a predictive encoding statistic. It is a different kind of number from a reverse inference
specificity map, so it is reported as its own estimate rather than merged with one.

Needs the neuroquery package and nilearn:
  pip install neuroquery nilearn

Writes:
  data/roi_zvalues.csv
  figures/roi_zvalues.png
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import rois

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
FIG = os.path.join(ROOT, "figures")
SPHERE_MM = 4.0
CORTICAL = "#b2182b"
SUBCORT = "#2166ac"


def get_map(result):
    for key in ("z_map", "brain_map", "raw_map"):
        if key in result and result[key] is not None:
            return result[key], key
    raise SystemExit("no map found in encoder result; keys were %s" % list(result))


def main():
    from neuroquery import fetch_neuroquery_model, NeuroQueryModel
    from nilearn.maskers import NiftiSpheresMasker

    encoder = NeuroQueryModel.from_data_dir(fetch_neuroquery_model())
    result = encoder("pain")
    img, key = get_map(result)
    print("using encoder map key:", key)

    roi = rois.extended()
    names = list(roi)
    coords = [(roi[n][0], roi[n][1], roi[n][2]) for n in names]
    kinds = [roi[n][3] for n in names]

    masker = NiftiSpheresMasker(seeds=coords, radius=SPHERE_MM, allow_overlap=True)
    vals = masker.fit_transform(img).ravel()

    res = pd.DataFrame({"roi": names, "kind": kinds, "z": vals}).sort_values(["kind", "z"],
                                                                             ascending=[True, False])
    res.to_csv(os.path.join(DATA, "roi_zvalues.csv"), index=False)
    print(res.to_string(index=False))

    order = res.sort_values("z")
    y = np.arange(len(order))
    cols = [CORTICAL if k == "cortical" else SUBCORT for k in order.kind]
    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.barh(y, order.z, color=cols, edgecolor="k", linewidth=0.4)
    ax.set_yticks(y)
    ax.set_yticklabels(order.roi)
    ax.set_xlabel("NeuroQuery encoding z for the query 'pain' (mean in a 4 mm sphere)")
    ax.set_title("Predictive encoding map for 'pain', read at the region coordinates")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "roi_zvalues.png"), dpi=200)
    plt.close(fig)

    prov = {"analysis": "B roi z sampling", "query": "pain", "map_key": key, "sphere_mm": SPHERE_MM}
    with open(os.path.join(DATA, "provenance_B.json"), "w") as f:
        json.dump(prov, f, indent=2)
    print("done")


if __name__ == "__main__":
    main()
