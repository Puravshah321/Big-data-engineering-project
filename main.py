from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import os
import threading

# -----------------------------
# App
# -----------------------------
app = FastAPI(title="Faculty Semantic Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "storage", "faculty.db")

# -----------------------------
# DB
# -----------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------------
# Startup checks + background ML
# -----------------------------
semantic_engine = None

@app.on_event("startup")
async def startup_event():

    if os.path.exists(DB_PATH):
        print("✅ Database found:", DB_PATH)
    else:
        print("❌ Database NOT found:", DB_PATH)

    def load_engine():
        global semantic_engine
        try:
            print("Initializing semantic engine in background thread...")
            from embeddings.vector_search import FacultyVectorSearch
            engine = FacultyVectorSearch()
            engine.load_data()
            semantic_engine = engine
            print("Semantic engine ready.")
        except Exception as e:
            print("Error loading semantic engine:", e)

    thread = threading.Thread(target=load_engine, daemon=True)
    thread.start()

# -----------------------------
# Healthcheck (CRITICAL)
# -----------------------------
@app.get("/health", include_in_schema=False)
def health_check():
    return {
        "status": "ok",
        "engine_ready": semantic_engine is not None
    }

# -----------------------------
# API Routes
# -----------------------------
@app.get("/")
def root():
    return {
        "message": "Faculty Search API running",
        "health": "/health"
    }

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
        "SELECT * FROM Faculty WHERE id = ?",
        (faculty_id,)
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Faculty not found")

    return dict(row)

@app.get("/semantic-search")
def semantic_search(
    q: str = Query(...),
    top_k: int = 5
):
    if semantic_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Search engine warming up, try again shortly"
        )

    results = semantic_engine.search(q, top_k)

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
# Serve React Frontend (SPA)
# -----------------------------
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

if os.path.exists(FRONTEND_DIST):
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")),
        name="assets"
    )

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    file_path = os.path.join(FRONTEND_DIST, full_path)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)

    return {"error": "Frontend build not found"}
