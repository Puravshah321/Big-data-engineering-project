import sqlite3
import pandas as pd
import sys
import os

# -----------------------------
# Fix import path
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from transform.clean_text import clean_text

# -----------------------------
# Constants
# -----------------------------
BASE_URL = "https://www.daiict.ac.in"

# -----------------------------
# Paths
# -----------------------------
CSV_PATH = os.path.join(BASE_DIR, "daiict_full_faculty_data.csv")
DB_PATH = os.path.join(BASE_DIR, "storage", "faculty.db")

# -----------------------------
# Load CSV
# -----------------------------
df = pd.read_csv(CSV_PATH)

# -----------------------------
# Build semantic_text
# -----------------------------
df["semantic_text"] = (
    df["Biography"].fillna("") + " " +
    df["Research Interests"].fillna("") + " " +
    df["Publications"].fillna("")
).apply(clean_text)

# -----------------------------
# Connect to SQLite
# -----------------------------
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# -----------------------------
# Insert data
# -----------------------------
# Clear existing data to avoid duplicates
cursor.execute("DELETE FROM Research_Tags")
cursor.execute("DELETE FROM Faculty")
# Reset Auto Increment
cursor.execute("DELETE FROM sqlite_sequence WHERE name='Faculty'")
cursor.execute("DELETE FROM sqlite_sequence WHERE name='Research_Tags'")

for _, row in df.iterrows():
    # Process Image URL
    image_url = row.get("Image URL")
    if pd.isna(image_url) or image_url == "N/A":
        image_url = None
    elif str(image_url).startswith("/"):
        image_url = BASE_URL + str(image_url)

    cursor.execute(
        """
        INSERT INTO Faculty (name, email, profile_url, image_url, qualification, semantic_text)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            row["Name"],
            row.get("Email"),
            row.get("Profile URL"),
            image_url,
            row.get("Qualification"),
            row["semantic_text"]
        )
    )

    faculty_id = cursor.lastrowid

    # Insert Specialization as Research Tags
    if pd.notna(row.get("Specialization")):
        for tag in str(row["Specialization"]).split(","):
            cursor.execute(
                """
                INSERT INTO Research_Tags (faculty_id, tag)
                VALUES (?, ?)
                """,
                (faculty_id, tag.strip())
            )

# -----------------------------
# Finalize
# -----------------------------
conn.commit()
conn.close()

print("✅ CSV data successfully loaded into storage/faculty.db")
