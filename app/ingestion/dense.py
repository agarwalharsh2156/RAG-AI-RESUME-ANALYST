from sentence_transformers import SentenceTransformer
from config import DENSE_MODEL_NAME

model = SentenceTransformer(DENSE_MODEL_NAME)
def dense_embed(query):
    """
        Requires a list of strings, each string specifying a specific chunk of the entire query(document, question).
    """
    embeddings = model.encode(query)
    return embeddings