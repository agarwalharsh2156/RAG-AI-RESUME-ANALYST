from sentence_transformers import SentenceTransformer
from config import DENSE_MODEL_NAME
from ingestion.parse import parse_pdf
from pathlib import Path


model = SentenceTransformer(DENSE_MODEL_NAME)
# model.save('./768-d-model')
# model.save('./384-d-model')
def create_query_for_embed(path):
    """
        Output format:
        {
            "file_name": {
                query: [list of sentences/chunks]
                metadata: [list of chunk names corresponding to the chunks in queries]
            }
        }
    """
    folder = Path(path)
    resumes = {}
    if folder.is_dir():
        for file in folder.glob("*.pdf"):
            resumes[file.name] = parse_pdf(file)
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

# ingestion/dense.py — at the end of dense_embed function
def dense_embed(path):
    """
        Expects a folder path. Input a folder which has all the resumes.
        Output format ->
        [
            {
                "id": "mohit_tcs_resume__personal_details", 
                "values": [...768 floats...], 
                "metadata": {
                    "filename": filename,
                    "section": section,
                    "resume_id": resume_id,
                    "text": texts[i][:1200]
                }
            }, 
            {
                "id": "mohit_tcs_resume__personal_details", 
                "values": [...768 floats...], 
                "metadata": {...}
            }, 

        ]
    """
    embed_queries = create_query_for_embed(path)
    to_upsert = []  

    for filename, data in embed_queries.items():
        texts = data["query"]          
        sections = data["metadata"]    

        if not texts:
            continue

        vectors = model.encode(texts, normalize_embeddings=True)  # shape (n_sections, 768)

        resume_id = filename.replace(".pdf", "").replace(" ", "_").lower()

        for i, (section, vector) in enumerate(zip(sections, vectors)):
            chunk_id = f"{resume_id}__{i}" 
            record = {
                "id": chunk_id,
                "values": vector.tolist(),              
                "metadata": {
                    "filename": filename,
                    "section": section,
                    "resume_id": resume_id,
                    "text": texts[i][:1200]              # truncate — Pinecone metadata limit ~40KB
                }
            }
            to_upsert.append(record)

    return to_upsert


if __name__ == "__main__":
    path = r".../resumes"
    result = dense_embed(path)
    print(result)

