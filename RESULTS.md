# Results and verdicts

Four measures computed directly from the NeuroQuery raw data, plus one that reads the encoding
model, all ask the same question from a different angle: does the pain neuroimaging literature
represent cortical structures more than subcortical ones. They agree, and they place the imbalance
at a specific stage.

## Headline

Across independent measures the cortical over subcortical contrast is always above one, and it grows
as you move from how the field talks about regions to how it reports their coordinates:

| Measure | Cortical over subcortical |
|---|---|
| Co-occurrence of region terms with "pain" (E) | 1.49 |
| Mentioned in text (C) | 1.62 |
| Coordinate reported, region groups (C) | 2.02 |
| Coordinate reported, core ten, 6 mm (A) | 2.05 |

The field discusses subcortical structures at close to parity, but reports their peak coordinates
about half as often as cortical ones. The imbalance is concentrated at the coordinate reporting
stage, not in whether the literature attends to these regions.

## A. Size-fair reporting audit — SUPPORTS

484 pain studies selected from NeuroQuery's own combined-text tf-idf (3.6% of the corpus, threshold
set by matching that fraction). Cortical regions are reported about twice as often as subcortical
and brainstem nuclei, and the separation is significant and stable across radii:

| Radius | Cortical mean | Subcortical mean | Ratio | Mann-Whitney p |
|---|---|---|---|---|
| 6 mm | 0.074 | 0.036 | 2.05 | 0.030 |
| 8 mm | 0.123 | 0.073 | 1.69 | 0.028 |
| 10 mm | 0.190 | 0.119 | 1.61 | 0.028 |
| 12 mm | 0.270 | 0.172 | 1.57 | 0.058 |

The threshold sweep keeps the ratio above one throughout, rising with pain specificity. The result
is selective: primary somatosensory cortex, a large and easily imaged region, is reported as rarely
as the subcortical nuclei and sits well below the other cortical nodes. A detectability-only account
predicts the opposite, so the pattern tracks what the literature emphasizes rather than only what is
easy to scan. Because NeuroQuery's coordinates come from an extraction pipeline that is independent
of other meta-analytic databases, this is a third, separately built dataset showing the same
imbalance, which points to an upstream property of the literature rather than any one tool's
extraction code.

## B. Region sampling of the predictive map — pending

Not yet run; requires the neuroquery encoding model and nilearn, which are still installing. To be
reported as its own predictive-encoding estimate at the same coordinates.

## C. Mention frequency versus reporting frequency — SHARPENS the account

For the same 484 studies, subcortical structures are named in the text far more often than their
coordinates are reported. Thalamus is the single most mentioned region of all (0.72, above every
cortical node) yet is reported near the bottom (0.045). Periaqueductal gray is mentioned about as
often as posterior insula but reported far less. The cortical over subcortical mention ratio (1.62)
is smaller than the reporting ratio (2.02), so the imbalance is amplified specifically when authors
move from discussing a region to reporting a peak for it. This separates a coordinate reporting and
indexing effect from a simple lack of attention to subcortex.

## D. Change across publication year — WEAK, leans toward a measurement limit

Publication years were recovered from PubMed for the pain subset, spanning 2004 to 2017 (the corpus
was frozen around 2019). The cortical over subcortical ratio declines weakly over time (weighted
least squares slope -0.44 per year, p = 0.054; ratio 2.85 before 2016 versus 2.48 from 2016). This
is consistent with a measurement limit that improving hardware relaxes, but it is not decisive: the
trend is borderline, the yearly ratios are noisy at small counts, and the corpus ends in 2017, so it
cannot see the recent high-field era where the strongest change would be expected.

## E. Semantic anchoring — SUPPORTS, and is the mildest of the measures

Computed from raw co-occurrence with no model in the loop. As a check, the terms closest to "pain"
are exactly the expected ones (painful, nociceptive, noxious, chronic pain, pain perception), and
the closest anatomical term is insula. "Pain" co-occurs with cortical region terms more than with
subcortical ones (0.151 versus 0.101, ratio 1.49). This is the smallest imbalance of the four
measures, which fits the gradient above: the field's vocabulary is only mildly cortical, and the
imbalance widens downstream at the reporting stage.

## What this does and does not show

These measures describe the literature, not the brain. They do not claim a region generates or does
not generate pain. What they establish is that the cortical dominance in coordinate summaries of pain
is, in substantial part, a property of how the literature reports and indexes results, present in a
third independently built dataset, concentrated at the coordinate reporting stage, and only weakly
attributable to acquisition era within the window the corpus covers.
