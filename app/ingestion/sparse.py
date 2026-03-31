import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer

# Where we save the fitted vectorizer after ingestion
# So retrieval can load it back without re-fitting
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "tfidf_vectorizer.pkl")


def fit_and_save_vectorizer(all_texts: list[str]):
    """
    Fit TF-IDF on all resume chunk texts and save to disk.
    Call this once during ingestion — not on every query.

    all_texts: flat list of every chunk text from every resume
    """
    vectorizer = TfidfVectorizer(
        max_features=30000,   # vocab size cap — enough for resume jargon
        sublinear_tf=True,    # log(1 + tf) instead of raw tf — better for long sections
        min_df=1              # keep rare tech terms (e.g. a niche framework in one resume)
    )
    vectorizer.fit(all_texts)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"TF-IDF vectorizer fitted on {len(all_texts)} chunks and saved to {VECTORIZER_PATH}")
    return vectorizer


def load_vectorizer():
    """
    Load the fitted vectorizer from disk.
    Called during retrieval so we don't re-fit every time.
    """
    if not os.path.exists(VECTORIZER_PATH):
        raise FileNotFoundError(
            f"Vectorizer not found at {VECTORIZER_PATH}. "
            "Run ingestion first(python -m app.ingestion.ingest) to fit and save the vectorizer."
        )
    return joblib.load(VECTORIZER_PATH)


def get_sparse_vector(text: str, vectorizer: TfidfVectorizer) -> dict:
    """
    Convert a single text into a Pinecone-compatible sparse vector.

    Returns:
        { "indices": [int, ...], "values": [float, ...] }
        indices = which vocubulary positions are non-zero
        values = the tf-idf weight at each of those positions
    """
    matrix = vectorizer.transform([text])
    row = matrix.getrow(0)
    return {
        "indices": row.indices.tolist(),
        "values": row.data.tolist()
    }