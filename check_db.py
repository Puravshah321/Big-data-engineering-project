import sqlite3
import os

db_path = 'storage/faculty.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT name FROM Faculty WHERE name LIKE '%Sourish%' OR semantic_text LIKE '%Sourish%'").fetchall()
    print(f"Found {len(rows)} matches for Sourish:")
    for row in rows:
        print(row[0])
    conn.close()
else:
    print("DB not found")
