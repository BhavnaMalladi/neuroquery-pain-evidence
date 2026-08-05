"""Download the NeuroQuery data tables into a local cache.

Set CACHE below to any folder on your machine. Files already present are skipped, so
rerunning is cheap. Nothing here needs a large model download; these are the plain
data tables published with the NeuroQuery dataset.
"""
import os
import time
import urllib.request

CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nq_cache")
BASE = "https://raw.githubusercontent.com/neuroquery/neuroquery_data/master/data/"

# local name -> remote file name
FILES = {
    "coordinates.tsv.gz": "data-neuroquery_version-1_coordinates.tsv.gz",
    "metadata.tsv.gz":    "data-neuroquery_version-1_metadata.tsv.gz",
    "tfidf_6308.npz":     "data-neuroquery_version-1_vocab-neuroquery6308_source-combined_type-tfidf_features.npz",
    "vocab_6308.txt":     "data-neuroquery_version-1_vocab-neuroquery6308_vocabulary.txt",
    "counts_abstract_7547.npz": "data-neuroquery_version-1_vocab-neuroquery7547_source-abstract_type-count_features.npz",
    "counts_body_7547.npz":     "data-neuroquery_version-1_vocab-neuroquery7547_source-body_type-count_features.npz",
    "counts_keywords_7547.npz": "data-neuroquery_version-1_vocab-neuroquery7547_source-keywords_type-count_features.npz",
    "counts_title_7547.npz":    "data-neuroquery_version-1_vocab-neuroquery7547_source-title_type-count_features.npz",
    "vocab_7547.txt":     "data-neuroquery_version-1_vocab-neuroquery7547_vocabulary.txt",
    "termcategories.csv": "data-neuroquery_version-1_termcategories.csv",
}


def download(url, dest, tries=5):
    for attempt in range(1, tries + 1):
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(dest, "wb") as f:
                while True:
                    chunk = r.read(1 << 16)
                    if not chunk:
                        break
                    f.write(chunk)
            return
        except Exception as e:
            if attempt == tries:
                raise
            wait = 3 * attempt
            print("  retry %d/%d after error: %s" % (attempt, tries, e))
            time.sleep(wait)


def main():
    os.makedirs(CACHE, exist_ok=True)
    for local, remote in FILES.items():
        dest = os.path.join(CACHE, local)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            print("have", local)
            continue
        print("get ", local)
        download(BASE + remote, dest)
    print("cache ready at", CACHE)


if __name__ == "__main__":
    main()
