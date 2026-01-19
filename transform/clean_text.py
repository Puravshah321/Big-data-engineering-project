"""
clean_text.py
--------------
Text cleaning utilities for faculty profile data.

Purpose:
- Normalize messy scraped HTML text
- Handle null / missing values safely
- Prepare text for NLP embedding & semantic search
"""

import re
import html
import pandas as pd


def clean_text(text: str) -> str:
    """
    Cleans raw scraped text and makes it NLP-ready.

    Steps:
    1. Handle nulls and placeholders
    2. Decode HTML entities
    3. Remove non-ASCII / control characters
    4. Normalize whitespace
    5. Strip leading/trailing spaces

    Parameters
    ----------
    text : str
        Raw scraped text

    Returns
    -------
    str
        Cleaned text
    """

    # ---------- Null & placeholder handling ----------
    if text is None:
        return ""

    if not isinstance(text, str):
        text = str(text)

    if text.strip().upper() in {"N/A", "NA", "NONE", "NULL"}:
        return ""

    # ---------- Decode HTML entities ----------
    text = html.unescape(text)

    # ---------- Remove control characters ----------
    text = re.sub(r"[\r\n\t]+", " ", text)

    # ---------- Remove non-ASCII characters ----------
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # ---------- Collapse multiple spaces ----------
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()


def build_semantic_text(row: pd.Series) -> str:
    """
    Combines multiple faculty text fields into one semantic string.

    Used for embedding generation.

    Parameters
    ----------
    row : pandas.Series
        Faculty row containing bio, research, publications

    Returns
    -------
    str
        Combined cleaned semantic text
    """

    fields = [
        row.get("Biography", ""),
        row.get("Research Interests", ""),
        row.get("Publications", "")
    ]

    cleaned_fields = [clean_text(field) for field in fields if field]

    return " ".join(cleaned_fields)


# ---------- Standalone execution (optional) ----------
if __name__ == "__main__":
    """
    Example usage:
    python clean_text.py
    """

    df = pd.read_csv("daiict_full_faculty_data.csv")

    df["semantic_text"] = df.apply(build_semantic_text, axis=1)

    df.to_csv("daiict_cleaned_faculty_data.csv", index=False)

    print("✅ Cleaned dataset saved as daiict_cleaned_faculty_data.csv")
