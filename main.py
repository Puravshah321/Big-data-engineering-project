from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import os
import threading
import time

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
        time.sleep(3) # Wait for uvicorn to be fully ready
        print("DEBUG: Starting background engine initialization...")
        try:
            from embeddings.vector_search import FacultyVectorSearch
            print(f"DEBUG: Importing FacultyVectorSearch success.")
            
            engine = FacultyVectorSearch()
            print(f"DEBUG: Initialized FacultyVectorSearch class.")
            
            engine.load_data()
            print(f"DEBUG: Data loaded successfully. Count: {len(engine.faculty_ids)}")
            
            if len(engine.faculty_ids) == 0:
                print("WARNING: Vector search loaded 0 records. Check database table 'Faculty'.")
            
            semantic_engine = engine
            print("✅ SUCCESS: Semantic engine is fully ready.")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print("❌ FATAL: Semantic engine failed to load:")
            print(error_details)
            # Store the error so we can see it in health check
            app.state.engine_error = str(e)

    app.state.engine_error = None
    thread = threading.Thread(target=load_engine, daemon=True)
    thread.start()

# -----------------------------
# Healthcheck (Detailed)
# -----------------------------
@app.get("/health")
def health_check():
    stats = {
        "status": "ok",
        "engine_ready": semantic_engine is not None,
        "engine_error": getattr(app.state, "engine_error", None),
        "db_exists": os.path.exists(DB_PATH),
    }
    if semantic_engine:
        stats["records_loaded"] = len(semantic_engine.faculty_ids)
    
    # Try a live DB count
    try:
        conn = get_db_connection()
        stats["db_count"] = conn.execute("SELECT COUNT(*) FROM Faculty").fetchone()[0]
        conn.close()
    except:
        stats["db_count"] = "error"
        
    return stats

# -----------------------------
# API Routes
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
