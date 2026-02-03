"""
vector_search.py
----------------
Semantic search over faculty profiles using user queries.
"""

import sqlite3
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# -----------------------------
# Absolute DB path (IMPORTANT)
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "storage", "faculty.db")

MODEL_NAME = "all-mpnet-base-v2"  # Better accuracy than MiniLM

class FacultyVectorSearch:
    def __init__(self):
        print(f"Loading semantic model: {MODEL_NAME}...")
        self.model = SentenceTransformer(MODEL_NAME)
        self.faculty_ids = []
        self.embeddings = []
        self.texts = []
        self.raw_data = [] # Store raw data for keyword matching

    def load_data(self):
        conn = sqlite3.connect(DB_PATH)
        # Fetch detailed data for keyword boosting
        rows = conn.execute(
            "SELECT id, semantic_text, name, qualification, image_url FROM Faculty WHERE semantic_text IS NOT NULL"
        ).fetchall()
        conn.close()

        if not rows:
            raise RuntimeError("No faculty data found in database.")

        self.faculty_ids = [row[0] for row in rows]
        self.texts = [row[1] for row in rows]
        # Store dicts for fast lookup/filtering if needed
        self.raw_data = [
            {"id": row[0], "text": row[1].lower(), "name": row[2].lower(), "qual": row[3].lower() if row[3] else "", "image": row[4]} 
            for row in rows
        ]

        # Generate embeddings
        print(f"Encoding {len(self.texts)} faculty profiles...")
        self.embeddings = self.model.encode(self.texts)
        print("Encoding complete.")

    def search(self, query: str, top_k: int = 5):
        query_embedding = self.model.encode([query])
        # Vector scores (Cosine Similarity)
        # Result is [ [score1, score2, ...] ]
        vector_scores = cosine_similarity(query_embedding, self.embeddings)[0]

        # Hybrid Scoring
        final_results = []
        query_lower = query.lower()
        query_terms = query_lower.split()

        for idx, score in enumerate(vector_scores):
            faculty_id = self.faculty_ids[idx]
            data = self.raw_data[idx]
            
            # Base vector score (typically 0.0 to 1.0)
            final_score = float(score)

            # 1. Name Match Boost (Huge boost for finding people)
            if query_lower in data["name"]:
                final_score += 0.5  
            
            # 2. Exact Phrase Match in Bio/Research (Significant boost)
            if query_lower in data["text"]:
                final_score += 0.2
                
            # 3. Term Overlap Boost (Small boost for coverage)
            # Count how many query terms appear in the text
            term_matches = sum(1 for term in query_terms if term in data["text"] or term in data["qual"])
            if len(query_terms) > 0:
                final_score += (term_matches / len(query_terms)) * 0.1

            final_results.append((faculty_id, final_score))

        # Re-rank based on hybrid score
        ranked = sorted(
            final_results,
            key=lambda x: x[1],
            reverse=True
        )

        return ranked[:top_k]


# -----------------------------
# CLI MODE (for testing)
# -----------------------------
if __name__ == "__main__":
    engine = FacultyVectorSearch()
    engine.load_data()

    print("\nFaculty Semantic Search")
    print("Type your question below (or type 'exit' to quit)\n")

    while True:
        query = input("Query: ").strip()

        if query.lower() in {"exit", "quit"}:
            print("Exiting search.")
            break

        if not query:
            print("Please enter a valid question.\n")
            continue

        results = engine.search(query)

        print("\nTop matching faculty:\n")
        for faculty_id, score in results:
            print(f"Faculty ID: {faculty_id} | Similarity: {score:.3f}")
        print("-" * 40)
