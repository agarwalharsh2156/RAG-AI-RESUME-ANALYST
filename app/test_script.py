from ingestion.dense import dense_embed

path = r"resumes"
results = dense_embed(path)

print(results)