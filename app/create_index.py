from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os
import config as c
load_dotenv()

# creating a pinecone object with the api key bypassing ssl certificate verification.
pc = Pinecone(api_key = os.getenv("PINECONE_AI_RESUME_ANALYST_KEY"), ssl_verify = False)
index_name = c.PINECONE_INDEX_NAME

# method to create a pinecone index
def create(index_name):
    # creating pinecone index is not exists
    if not pc.has_index(index_name):
        pc.create_index(
            name = index_name,
            vector_type = c.PINECONE_VECTOR_TYPE,
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

        print(f"Pinecone index created with name: {index_name}")
        return

    print("Pinecone index already exists.")
    return

if __name__ == "__main__":
    request = input("Create or Delete (C or D): ").strip().lower()

    if request == "c":
        if pc.has_index(index_name):
            print(f"Index '{index_name}' already exists.")
        else:
            create(index_name=index_name)

    elif request == "d":
        if pc.has_index(index_name):
            pc.delete_index(index_name)
            print(f"Deleted index: {index_name}")
        else:
            print(f"Index '{index_name}' does not exist.")

    else:
        print("Invalid option. Please enter C or D.")