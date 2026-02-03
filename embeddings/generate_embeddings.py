import sqlite3
import os
import numpy as np
import json
from sentence_transformers import SentenceTransformer

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "storage", "faculty.db")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "embeddings", "embeddings.npy")
METADATA_PATH = os.path.join(BASE_DIR, "embeddings", "metadata.json")

MODEL_NAME = "all-MiniLM-L6-v2"

def generate():
    print("Generating embeddings locally...")
    model = SentenceTransformer(MODEL_NAME)
    
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT id, semantic_text, name, qualification FROM Faculty").fetchall()
    conn.close()
    
    ids = []
    texts = []
    raw_data = []
    
    for r in rows:
        if r[1] and len(r[1].strip()) > 0:
            ids.append(r[0])
            truncated = r[1][:500].strip()
            texts.append(truncated)
            raw_data.append({
                "id": r[0],
                "text": truncated.lower(),
                "name": r[2].lower(),
                "qual": r[3].lower() if r[3] else ""
            })
            
    print(f"Encoding {len(texts)} records...")
    embeddings = model.encode(texts, batch_size=1, convert_to_numpy=True).astype(np.float16)
    
    # Save files
    np.save(EMBEDDINGS_PATH, embeddings)
    with open(METADATA_PATH, "w") as f:
        json.dump({"ids": ids, "raw_data": raw_data}, f)
        
    print(f"✅ Success! Saved {len(ids)} embeddings to {EMBEDDINGS_PATH}")

if __name__ == "__main__":
    generate()
