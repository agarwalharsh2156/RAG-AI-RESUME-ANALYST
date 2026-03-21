from pinecone import Pinecone
from dotenv import load_dotenv
import os 
from config import PINECONE_INDEX_NAME, RESUME_DIR
from ingestion.dense import dense_embed

load_dotenv()

def upsert_to_index(path):
    records = dense_embed(path)
    if not records:
        print("No records to upsert")
        return []
    
    pc = Pinecone(api_key= os.getenv("PINECONE_AI_RESUME_ANALYST_KEY"), ssl_verify= False)
    index = pc.Index(PINECONE_INDEX_NAME)

    if not index:
        print("Index not available. Couldn't upsert")
        return records
    
    index.upsert(vectors= records)
    print("Successfully upserted")
    return records

if __name__=="__main__":
    folder_path = RESUME_DIR
    records = upsert_to_index(folder_path)
    print(f"First record upserted: {records[0]}")