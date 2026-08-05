# Representation bias in the NeuroQuery pain corpus

How does the human pain neuroimaging literature represent deep brain structures relative to
cortical ones? This project measures that directly from the NeuroQuery open dataset, which ships
peak activation coordinates, per-study term frequencies, raw word counts, article metadata, and a
term co-occurrence matrix for roughly 13,000 neuroimaging papers. NeuroQuery built these tables
with its own full-text extraction pipeline, independent of other meta-analytic databases, and
reports substantially fewer coordinate extraction errors than earlier abstract-based tools (Dockes
et al., 2020, Table 2). That makes the raw dataset a useful, independent lens on the literature.

Everything here works from the downloaded tables by counting and simple statistics. No trained
query model sits between the analysis and the result, except in one clearly marked place (analysis
B), so the known failure modes of the predictive query interface do not apply.

## The five analyses

- **A. Size-fair reporting audit.** For a set of a priori pain regions, measure the fraction of
  pain studies that report a peak within a fixed-radius sphere at each region. The radius is the
  same for every region, so a region is not favored for being large. Compare cortical to
  subcortical and brainstem nodes across radii of 6, 8, 10 and 12 mm.
- **B. Region sampling of the predictive map.** Run the single reference term "pain" through the
  NeuroQuery encoding model and read its rescaled z at the same region coordinates. This is the one
  analysis that uses the trained model, held to a single validated term sampled at fixed
  coordinates.
- **C. Mention frequency versus reporting frequency.** Using raw word counts, measure how often each
  region is named in the text at all, and compare that to how often a coordinate is actually
  reported for it. A gap separates a discussion bias from a coordinate reporting bias.
- **D. Change across publication year.** Split the pain corpus by year and test whether the
  cortical to subcortical reporting ratio shrinks over time, which would point to a measurement
  limit that better hardware relaxes, or stays flat, which would point to a reporting habit.
- **E. Semantic anchoring.** Using the term co-occurrence matrix, measure whether "pain" sits closer
  to cortical terms than to subcortical terms in the field's own vocabulary structure.

## Running it

The notebook `neuroquery_evidence.ipynb` reads the precomputed tables in `data/` and reproduces
every figure without a large download. To rebuild the tables from scratch, run the scripts in `src/`
in order; the first one fetches the NeuroQuery data into a local cache folder you set at the top.

```
python src/fetch_data.py
python src/audit_reporting.py
python src/roi_zsample.py
python src/year_trend.py
python src/mention_counts.py
python src/semantic_anchoring.py
python src/make_figures.py
```

## Layout

```
data/       precomputed result tables and provenance.json
src/        one script per analysis, plus fetch and figures
figures/    generated figures
```

## Data and citation

Raw data: NeuroQuery data repository, https://github.com/neuroquery/neuroquery_data
Dataset and methods: Dockes J, Poldrack RA, Primet R, et al. NeuroQuery, comprehensive
meta-analysis of human brain mapping. eLife 2020;9:e53385.


