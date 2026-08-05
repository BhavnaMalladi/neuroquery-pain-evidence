# Sources and credit

## Data

NeuroQuery dataset (coordinates, term frequencies, word counts, metadata, vocabulary):
Dockes J, Poldrack RA, Primet R, Gozukan H, Yarkoni T, Suchanek F, Thirion B, Varoquaux G.
NeuroQuery, comprehensive meta-analysis of human brain mapping. eLife 2020;9:e53385.
https://doi.org/10.7554/eLife.53385
Repository: https://github.com/neuroquery/neuroquery_data

Publication years for the pain study subset were retrieved from PubMed with the NCBI E-utilities
esummary service (https://www.ncbi.nlm.nih.gov/books/NBK25501/), keyed on the PubMed identifiers
shipped in the NeuroQuery metadata.

## Region coordinates

The core ten node set follows the standard cortical and subcortical pain regions used across pain
imaging meta-analyses. Representative sources for the pain peak coordinates and the brainstem nuclei:

- Duerden EG, Albanese MC. Localization of pain-related brain activation: a meta-analysis of
  neuroimaging data. Human Brain Mapping 2013;34(1):109-149.
- Tanasescu R, Cottam WJ, Condon L, Tench CR, Auer DP. Functional reorganisation in chronic pain and
  neural correlates of pain sensitisation: a coordinate based meta-analysis. Neuroscience and
  Biobehavioral Reviews 2016;68:120-133.
- Bianciardi M, et al. Toward an in vivo neuroimaging template of human brainstem nuclei of the
  ascending arousal, autonomic, and motor systems (Brainstem Navigator). Brain Connectivity and
  related atlas releases.

Each coordinate is a literature-approximate centre. The audit uses a fixed sphere radius at every
centre, so reporting rate does not depend on the true extent of the region.

## Software

- NumPy, SciPy, pandas, Matplotlib, statsmodels, scikit-learn.
- nilearn (region sampling of the encoding map): https://nilearn.github.io
- neuroquery python package (encoding model, used only in Idea B):
  https://github.com/neuroquery/neuroquery

## Reuse

If you reuse a piece, cite the matching source above. Add a LICENSE file before sharing the code.
