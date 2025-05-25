from flask import Flask, render_template, request
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np

app = Flask(__name__)

# Load data
advisors_df = pd.read_csv("data/authors.csv")
papers_df = pd.read_csv("data/papers(example).csv")

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Preprocess papers to generate embeddings
def preprocess_papers(df):
    def embed(row):
        return model.encode(row['title'] + " " + row['abstract'])
    df['embedding'] = df.apply(embed, axis=1)
    return df

papers_df = preprocess_papers(papers_df)

# Cosine similarity
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    query = ""
    if request.method == "POST":
        query = request.form["query"]
        query_embedding = model.encode(query)

        # Compute similarity
        for _, row in papers_df.iterrows():
            sim = cosine_similarity(query_embedding, row['embedding'])
            results.append({
                "title": row['title'],
                "abstract": row['abstract'],
                "score": round(sim, 3),
                "advisor_id": row['advisor_scholar_id']
            })

        # Sort by similarity
        results.sort(key=lambda x: x["score"], reverse=True)

    return render_template("index.html", results=results, query=query)

if __name__ == "__main__":
    app.run(debug=True)
