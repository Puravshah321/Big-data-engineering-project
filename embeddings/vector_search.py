"""
vector_search.py
----------------
Semantic search over faculty profiles optimized for Railway (500MB RAM).
"""

import sqlite3
import os
import numpy as np
from sentence_transformers import SentenceTransformer

# -----------------------------
# Absolute DB path
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "storage", "faculty.db")

MODEL_NAME = "all-MiniLM-L6-v2"

def cosine_similarity_manual(v1, v2):
    # v1 (query) is [1, D], v2 (database) is [N, D]
    # We flatten for safe division
    v1_fixed = v1.reshape(1, -1)
    
    dot_product = np.dot(v1_fixed, v2.T).flatten() # [N]
    
    norm_v1 = np.linalg.norm(v1_fixed) # scalar
    norm_v2 = np.linalg.norm(v2, axis=1) # [N]
    
    denominator = norm_v1 * norm_v2
    # Prevent divide by zero
    denominator[denominator == 0] = 1e-8
    
    return dot_product / denominator

class FacultyVectorSearch:
    def __init__(self):
        print(f"DEBUG: Loading model {MODEL_NAME}...")
        self.model = SentenceTransformer(MODEL_NAME)
        self.faculty_ids = []
        self.embeddings = []
        self.texts = []
        self.raw_data = []

    def load_data(self):
        conn = sqlite3.connect(DB_PATH)
        # Fetch all rows where semantic_text is not null
        rows = conn.execute(
            "SELECT id, semantic_text, name, qualification, image_url FROM Faculty"
        ).fetchall()
        conn.close()

        if not rows:
            raise RuntimeError("No faculty data found in database.")

        # Filter out empty semantic texts and keep track of IDs
        valid_records = []
        for r in rows:
            if r[1] and len(r[1].strip()) > 0:
                valid_records.append(r)

        self.faculty_ids = [r[0] for r in valid_records]
        self.texts = [r[1] for r in valid_records]
        self.raw_data = [
            {"id": r[0], "text": r[1].lower(), "name": r[2].lower(), "qual": r[3].lower() if r[3] else "", "image": r[4]} 
            for r in valid_records
        ]

        print(f"DEBUG: Encoding {len(self.texts)} records (batch_size=1)...")
        # Optimization: convert to float16 to save significant RAM
        self.embeddings = self.model.encode(
            self.texts, 
            batch_size=1, 
            show_progress_bar=False,
            convert_to_numpy=True
        ).astype(np.float16)
        print("DEBUG: Encoding complete.")

    def search(self, query: str, top_k: int = 5):
        if len(self.embeddings) == 0:
            return []
            
        query_embedding = self.model.encode([query], convert_to_numpy=True).astype(np.float16)
        scores = cosine_similarity_manual(query_embedding, self.embeddings)

        final_results = []
        query_lower = query.lower()
        query_terms = query_lower.split()

        for idx, score in enumerate(scores):
            faculty_id = self.faculty_ids[idx]
            data = self.raw_data[idx]
            
            final_score = float(score)

            # Name Match Boost
            if query_lower in data["name"]:
                final_score += 0.5  
            
            # Phrase Match Boost
            if query_lower in data["text"]:
                final_score += 0.2
                
            # Term Overlap Boost
            term_matches = sum(1 for term in query_terms if term in data["text"] or term in data["qual"])
            if len(query_terms) > 0:
                final_score += (term_matches / len(query_terms)) * 0.1

            final_results.append((faculty_id, final_score))

        # Re-rank
        ranked = sorted(final_results, key=lambda x: x[1], reverse=True)
        return ranked[:top_k]
