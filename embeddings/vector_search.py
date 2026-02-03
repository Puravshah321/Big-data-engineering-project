"""
vector_search.py
----------------
Semantic search over faculty profiles optimized for Railway (500MB RAM).
Uses pre-computed embeddings if available to save RAM/CPU on startup.
"""

import sqlite3
import os
import gc
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# -----------------------------
# Absolute Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "storage", "faculty.db")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "embeddings", "embeddings.npy")
METADATA_PATH = os.path.join(BASE_DIR, "embeddings", "metadata.json")

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
        # 1. Check if we have pre-computed embeddings
        if os.path.exists(EMBEDDINGS_PATH) and os.path.exists(METADATA_PATH):
            print(f"DEBUG: Loading PRE-COMPUTED embeddings from {EMBEDDINGS_PATH}...")
            self.embeddings = np.load(EMBEDDINGS_PATH)
            with open(METADATA_PATH, "r") as f:
                meta = json.load(f)
                self.faculty_ids = meta["ids"]
                self.raw_data = meta["raw_data"]
            print(f"✅ SUCCESS: Loaded {len(self.faculty_ids)} embeddings from disk.")
            return

        # 2. Fallback to manual encoding if files are missing
        print("DEBUG: Pre-computed files not found. Falling back to manual encoding...")
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT id, semantic_text, name, qualification FROM Faculty"
        ).fetchall()
        conn.close()

        if not rows:
            raise RuntimeError("No faculty data found in database.")

        texts = []
        for r in rows:
            content = r[1]
            if content and len(content.strip()) > 0:
                self.faculty_ids.append(r[0])
                truncated_text = content[:500].strip()
                texts.append(truncated_text)
                self.raw_data.append({
                    "id": r[0],
                    "text": truncated_text.lower(),
                    "name": r[2].lower(),
                    "qual": r[3].lower() if r[3] else "",
                })
        
        del rows
        gc.collect()

        dim = 384
        self.embeddings = np.zeros((len(texts), dim), dtype=np.float16)
        
        for i, text in enumerate(texts):
            vec = self.model.encode([text], show_progress_bar=False, convert_to_numpy=True)
            self.embeddings[i] = vec[0].astype(np.float16)
        
        del texts
        gc.collect()
        print("DEBUG: Encoding complete.")

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
