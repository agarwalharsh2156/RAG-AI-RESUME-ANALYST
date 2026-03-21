from pinecone import Pinecone
from config import PINECONE_INDEX_NAME # adjust import as needed
import os
from dotenv import load_dotenv
load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_AI_RESUME_ANALYST_KEY"), ssl_verify= False)
index = pc.Index(PINECONE_INDEX_NAME)

stats = index.describe_index_stats()
print(stats)