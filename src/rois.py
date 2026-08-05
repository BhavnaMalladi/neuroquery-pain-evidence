"""A priori pain regions of interest in MNI152 space.

The core set is the standard ten node pain comparison: five cortical nodes and five
subcortical or brainstem nuclei. The extended set adds three cortical and three
subcortical regions, chosen to sit well away from the core nodes and from each other,
so the audit can be repeated on a broader and still balanced panel.

Every coordinate is a literature approximate centre. The audit places a sphere of the
same radius at each centre, so a region is never favored for being large.
"""

# name: (x, y, z, class), MNI152 in millimetres
CORE = {
    "dACC":         (0, 24, 28, "cortical"),
    "aInsula_L":    (-38, 6, 2, "cortical"),
    "aInsula_R":    (38, 6, 2, "cortical"),
    "S1":           (-40, -30, 55, "cortical"),
    "S2":           (-50, -22, 18, "cortical"),
    "Thalamus":     (0, -16, 6, "subcortical"),
    "PAG":          (0, -29, -12, "subcortical"),
    "Parabrachial": (6, -37, -26, "subcortical"),
    "Hypothalamus": (0, -4, -12, "subcortical"),
    "Amygdala":     (-24, -4, -18, "subcortical"),
}

# Additions kept spatially distinct from the core and balanced across class.
# Posterior insula and anterior mid cingulate on the cortical side; rostral
# ventromedial medulla and ventral striatum on the subcortical side.
EXTENDED_ADD = {
    "pInsula_L":    (-38, -18, 10, "cortical"),
    "pInsula_R":    (38, -18, 10, "cortical"),
    "aMCC":         (0, 20, 34, "cortical"),
    "RVM":          (0, -34, -48, "subcortical"),
    "NAc_L":        (-10, 12, -6, "subcortical"),
    "NAc_R":        (10, 12, -6, "subcortical"),
}


def core():
    return dict(CORE)


def extended():
    d = dict(CORE)
    d.update(EXTENDED_ADD)
    return d


def as_frame(roi_dict):
    import pandas as pd
    rows = [(n, x, y, z, k) for n, (x, y, z, k) in roi_dict.items()]
    return pd.DataFrame(rows, columns=["roi", "x", "y", "z", "kind"])
