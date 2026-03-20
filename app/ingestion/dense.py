from sentence_transformers import SentenceTransformer
from config import DENSE_MODEL_NAME
from ingestion.parse import parse_pdf
from pathlib import Path


model = SentenceTransformer(DENSE_MODEL_NAME)
def create_query_for_embed(path):
    """
        Output format:
        {
            file_name: {
                query: [list of sentences/chunks]
                metadata: [list of chunk names corresponding to the chunks in queries]
            }
        }
    """
    folder = Path(path)
    resumes = {}
    if folder.is_dir():
        for file in folder.glob("*.pdf"):
            resumes[file.name] = parse_pdf(folder)
    else:
        print("Folder doesn't exist")
        return {}

    embed_queries = {}

    for key in resumes.keys():
        resume = resumes[key]
        query = []
        query.extend(resume.values())
        chunks = []
        chunks.extend(resume.keys())
        embed_queries[key] = {"query": query}
        embed_queries[key]["metadata"] = chunks 
    return embed_queries

def dense_embed(path):
    """
        Requires a list of strings, each string specifying a specific chunk of the entire query(document, question).
    """
    embed_queries = create_query_for_embed(path)
    embeddings = {

    }
    for key, value in embed_queries.entries():
        file_name = key
        query = value["query"]
        chunk_names = value["metadata"]
        embeddings["file_name"] = file_name
        embeddings["dense"] = model.encode(query)
        embeddings["metadata"] = chunk_names
    return embeddings

if __name__ == "main":
    path = r"C:\Projects\AI_Resume_Analyst\resumes"
    result = dense_embed(path)
    print(result)

