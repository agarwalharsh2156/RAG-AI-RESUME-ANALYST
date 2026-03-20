from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os
import config as c
load_dotenv()

# method to create a pinecone index
def create():
    # creating a pinecone object with the api key bypassing ssl certificate verification.
    pc = Pinecone(api_key = os.getenv("PINECONE_AI_RESUME_ANALYST_KEY"), ssl_verify = False)

    # setting Pinecone index name
    index_name = c.PINECONE_INDEX_NAME

    # creating pinecone index is not exists
    if not pc.has_index(index_name):
        pc.create_index(
            name = index_name,
            
            # specifying if want elastic scaling or Pod based customised resource specifications
            spec = ServerlessSpec(
                cloud = c.PINECONE_INDEX_CLOUD,
                region = c.PINECONE_INDEX_REGION
            ),

            # same as the dimensions of dense vector embedding creation model
            dimension= c.PINECONE_INDEX_DIMENSION,

            # metric for specifying hybrid searching (semantic + lexical/keyword). 
            # metric = "dotproduct" allows storing both dense and sparse vectors.
            metric = c.PINECONE_INDEX_METRIC, 
        )

    return f"Pinecone index created with name: {index_name}"

if __name__ == "main":
    create()
