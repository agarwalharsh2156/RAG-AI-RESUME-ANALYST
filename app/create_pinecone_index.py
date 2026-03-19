from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os
import config as c
load_dotenv()

# method to create a pinecone index
def create_index():
    pc = Pinecone(api_key = os.getenv("PINECONE_AI_RESUME_ANALYST_KEY"))

    index_name = c.PINECONE_INDEX_NAME

    if not pc.has_index(index_name):
        pc.create_index(
            name = index_name,
            spec = ServerlessSpec(
                cloud = c.PINECONE_INDEX_CLOUD,
                region = c.PINECONE_INDEX_REGION
            ),
            dimension= c.PINECONE_INDEX_DIMENSION,
            metric = c.PINECONE_INDEX_METRIC
        )

    return f"Pinecone index created with name: {index_name}"


if __name__ == "main":
    create_index()