from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer()
def spare_embed(query):
    results = vectorizer.fit_transform(query)
    return results 
