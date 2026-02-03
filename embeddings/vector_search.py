"""
vector_search.py
----------------
Semantic search over faculty profiles optimized for Railway (500MB RAM).
"""

import sqlite3
import os
import gc
import numpy as np
from sentence_transformers import SentenceTransformer

# -----------------------------
# Absolute DB path
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "storage", "faculty.db")

MODEL_NAME = "all-MiniLM-L6-v2"

def cosine_similarity_manual(v1, v2):
    v1_fixed = v1.reshape(1, -1)
    dot_product = np.dot(v1_fixed, v2.T).flatten()
    norm_v1 = np.linalg.norm(v1_fixed)
    norm_v2 = np.linalg.norm(v2, axis=1)
    denominator = norm_v1 * norm_v2
    denominator[denominator == 0] = 1e-8
    return dot_product / denominator

class FacultyVectorSearch:
    def __init__(self):
        print(f"DEBUG: Loading model {MODEL_NAME}...")
        self.model = SentenceTransformer(MODEL_NAME)
        self.faculty_ids = []
        self.embeddings = None
        self.raw_data = []

    def load_data(self):
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT id, semantic_text, name, qualification, image_url FROM Faculty"
        ).fetchall()
        conn.close()

        if not rows:
            raise RuntimeError("No faculty data found in database.")

        texts = []
        for r in rows:
            if r[1] and len(r[1].strip()) > 0:
                self.faculty_ids.append(r[0])
                texts.append(r[1])
                self.raw_data.append({
                    "id": r[0],
                    "text": r[1].lower(),
                    "name": r[2].lower(),
                    "qual": r[3].lower() if r[3] else "",
                })
        
        del rows
        gc.collect()

        print(f"DEBUG: Encoding {len(texts)} records one-by-one to save RAM...")
        # Pre-allocate float16 array
        dim = 384 # Dimension for all-MiniLM-L6-v2
        self.embeddings = np.zeros((len(texts), dim), dtype=np.float16)
        
        # Encode one by one to avoid large intermediate buffers
        for i, text in enumerate(texts):
            # Encode single text, convert to f16 immediately
            vec = self.model.encode([text], show_progress_bar=False, convert_to_numpy=True)
            self.embeddings[i] = vec[0].astype(np.float16)
            if i % 20 == 0:
                print(f"DEBUG: Encoded {i}/{len(texts)}...")
        
        del texts
        gc.collect()
        print("DEBUG: Encoding complete. Memory cleared.")

    def search(self, query: str, top_k: int = 5):
        if self.embeddings is None:
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

            if query_lower in data["name"]:
                final_score += 0.5  
            if query_lower in data["text"]:
                final_score += 0.2
            
            term_matches = sum(1 for term in query_terms if term in data["text"] or term in data["qual"])
            if len(query_terms) > 0:
                final_score += (term_matches / len(query_terms)) * 0.1

            final_results.append((faculty_id, final_score))

        ranked = sorted(final_results, key=lambda x: x[1], reverse=True)
        return ranked[:top_k]
