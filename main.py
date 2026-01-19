from fastapi import FastAPI, Query
import sqlite3
import os

# -----------------------------
# App
# -----------------------------
app = FastAPI(title="Faculty Semantic Search API")

# -----------------------------
# Absolute DB path
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "storage", "faculty.db")

# -----------------------------
# DB connection
# -----------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------------
# SQL Endpoints
# -----------------------------
@app.get("/faculty")
def get_all_faculty():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM Faculty").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/faculty/{faculty_id}")
def get_faculty_by_id(faculty_id: int):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM Faculty WHERE id = ?", (faculty_id,)
    ).fetchone()
    conn.close()

    if not row:
        return {"error": "Faculty not found"}

    return dict(row)

# -----------------------------
# Semantic Search Integration
# -----------------------------
from embeddings.vector_search import FacultyVectorSearch

semantic_engine = FacultyVectorSearch()
semantic_engine.load_data()

@app.get("/semantic-search")
def semantic_search(
    q: str = Query(..., description="Search query"),
    top_k: int = 5
):
    results = semantic_engine.search(q, top_k)

    # Convert faculty IDs to full records
    conn = get_db_connection()
    output = []

    for faculty_id, score in results:
        row = conn.execute(
            "SELECT id, name, email, qualification FROM Faculty WHERE id = ?",
            (faculty_id,)
        ).fetchone()

        if row:
            data = dict(row)
            data["similarity"] = round(float(score), 4)
            output.append(data)

    conn.close()
    return output
