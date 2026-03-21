# from sklearn.feature_extraction.text import TfidfVectorizer

# vectorizer = TfidfVectorizer()
# def spare_embed(query):
#     results = vectorizer.fit_transform(query)
#     return results 


from sklearn.feature_extraction.text import TfidfVectorizer
from pathlib import Path
from app.ingestion.parse import parse_pdf


def create_query_for_sparse(path):
    folder = Path(path)
    resumes = {}

    if folder.is_dir():
        for file in folder.glob("*.pdf"):
            resumes[file.name] = parse_pdf(file)
    else:
        print("Folder doesn't exist")
        return {}

    sparse_queries = {}

    for key in resumes.keys():
        resume = resumes[key]
        query = list(resume.values())
        chunks = list(resume.keys())

        sparse_queries[key] = {
            "query": query,
            "metadata": chunks
        }

    return sparse_queries


def sparse_embed(path):
    sparse_queries = create_query_for_sparse(path)

    all_texts = []
    all_info = []

    for file_name, value in sparse_queries.items():
        query = value["query"]
        chunk_names = value["metadata"]
        resume_id = Path(file_name).stem

        for chunk_name, chunk_text in zip(chunk_names, query):
            all_texts.append(chunk_text)
            all_info.append({
                "id": f"{file_name}_{chunk_name.lower().replace(' ', '_')}",
                "filename": file_name,
                "section": chunk_name,
                "text": chunk_text,
                "resume_id": resume_id
            })

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    sparse_output = {}

    for i, info in enumerate(all_info):
        row = tfidf_matrix.getrow(i)

        record = {
            "id": info["id"],
            "sparse_values": {
                "indices": row.indices.tolist(),
                "values": row.data.tolist()
            },
            "metadata": {
                "filename": info["filename"],
                "section": info["section"],
                "text": info["text"],
                "resume_id": info["resume_id"]
            }
        }

        file_name = info["filename"]
        if file_name not in sparse_output:
            sparse_output[file_name] = []

        sparse_output[file_name].append(record)

    return sparse_output, vectorizer


def sparse_query_embed(query_text, vectorizer):
    row = vectorizer.transform([query_text]).getrow(0)
    return {
        "indices": row.indices.tolist(),
        "values": row.data.tolist()
    }


if __name__ == "__main__":
    path = r"C:\Projects\AI_Resume_Analyst\resumes"
    result, vectorizer = sparse_embed(path)
    print(result)
