from fastapi import FastAPI, Query
import sqlite3
import os

# -----------------------------
# App
# -----------------------------
app = FastAPI(title="Faculty Semantic Search API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            "SELECT id, name, email, qualification, profile_url, image_url FROM Faculty WHERE id = ?",
            (faculty_id,)
        ).fetchone()

        if row:
            data = dict(row)
            data["similarity"] = round(float(score), 4)
            output.append(data)

    conn.close()
    return output

# -----------------------------
# Serve Frontend (SPA)
# -----------------------------
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount the static directory
# Ensure 'frontend/dist' exists (it will be populated in the Docker build or local build)
if os.path.exists(os.path.join(BASE_DIR, "frontend", "dist")):
    app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, "frontend", "dist", "assets")), name="assets")

# Catch-all route to serve index.html for any unmatched route (important for React Router/SPA)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    # If the path matches a file in dist (e.g. favicon.ico), serve it
    dist_path = os.path.join(BASE_DIR, "frontend", "dist", full_path)
    if os.path.exists(dist_path) and os.path.isfile(dist_path):
        return FileResponse(dist_path)
    
    # Otherwise, serve index.html
    index_path = os.path.join(BASE_DIR, "frontend", "dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"error": "Frontend not found. Did you run 'npm run build'?"}
