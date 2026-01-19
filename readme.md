Below is a **clean, professional, copy-paste-ready `README.md`** written for **academic submission + GitHub review**.
It clearly explains **what was done**, shows the **pipeline**, cites the **data source**, and includes the **contributors exactly as you asked**.

You can **copy everything as-is** and paste it into `README.md`.

---

```markdown
# Faculty Semantic Search Data Pipeline

## 📌 Project Overview
This project implements an **end-to-end data engineering pipeline** to crawl, extract, clean, and store faculty profile data from a college website and enable **semantic (meaning-based) search** over the data.

The pipeline converts **unstructured HTML data** into a **clean, structured dataset**, generates **text embeddings**, and exposes the results through a **FastAPI-based REST service**.

This project is developed as part of a **Big Data Engineering (BDE)** academic assignment.

---

## 🎯 Objectives
- Crawl faculty profile data from a public academic website  
- Extract structured information such as names, bios, and research interests  
- Clean and normalize noisy textual data  
- Store curated data in a relational database  
- Enable semantic search using NLP embeddings  
- Serve data and search results via REST APIs  

---

## 🌐 Data Source
Faculty data was scraped from the official DA-IICT faculty directory:

🔗 **Source URL:**  
https://www.daiict.ac.in/faculty  

> The data has been used strictly for **academic and educational purposes only**.

---

## 🧱 Data Pipeline Architecture

project/pipeline bde.png

---

## ⚙️ Pipeline Stages Explained

### 1️⃣ Web Crawling & Extraction
- Crawls faculty profile pages from the DA-IICT website
- Extracted fields include:
  - Name
  - Email
  - Qualification
  - Biography
  - Research Interests
  - Publications

**Output:**  
Raw structured CSV file:  
`daiict_full_faculty_data.csv`

---

### 2️⃣ Data Cleaning & Transformation
- Removes HTML artifacts and noise
- Normalizes whitespace and encoding
- Handles missing and null values
- Combines multiple text fields into a single **semantic_text** field for NLP tasks

📂 Implemented in:
```

transform/clean_text.py

```

---

### 3️⃣ Data Storage (SQLite)
A lightweight SQLite database is used for persistent storage.

**Tables:**
- `Faculty` – stores core faculty information and semantic text
- `Research_Tags` – stores specialization/research areas

📂 Schema:
```

storage/schema.sql

```

📂 Data ingestion:
```

storage/load_csv_to_sqlite.py

```

---

### 4️⃣ Embedding Generation
- Uses a pretrained transformer model to convert text into dense vectors
- Model used:
```

all-MiniLM-L6-v2

```

- Embeddings are generated from the `semantic_text` field

📂 Implemented in:
```

embeddings/vector_search.py

```

---

### 5️⃣ Semantic Search Engine
- Converts user queries into embeddings
- Uses **cosine similarity** to rank faculty profiles
- Enables meaning-based retrieval rather than keyword matching

Example queries:
- *machine learning faculty*
- *wireless networks*
- *computer vision research*

---

### 6️⃣ API Layer (FastAPI)
The backend exposes the following REST endpoints:

- `/faculty` – Retrieve all faculty records  
- `/faculty/{id}` – Retrieve a faculty record by ID  
- `/semantic-search?q=` – Perform semantic search  

Swagger UI available at:
```

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

```

📂 Implemented in:
```

main.py

```

---

## 🗂️ Project Structure

```

project/
├── embeddings/
│   └── vector_search.py
├── transform/
│   └── clean_text.py
├── storage/
│   ├── faculty.db
│   ├── schema.sql
│   └── load_csv_to_sqlite.py
├── daiict_full_faculty_data.csv
├── main.py
├── requirements.txt
└── README.md

````

---

## 🚀 How to Run the Project

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
````

---

### 2️⃣ Create Database & Load Data

```bash
sqlite3 storage/faculty.db
.read storage/schema.sql
.exit

python storage/load_csv_to_sqlite.py
```

---

### 3️⃣ Run FastAPI Server

```bash
uvicorn main:app --reload
```

---

### 4️⃣ Run Semantic Search (CLI Mode)

```bash
python embeddings/vector_search.py
```

---

## 🧠 Key Technologies Used

* Python
* SQLite
* Pandas
* Requests
* BeautifulSoup
* FastAPI
* SentenceTransformers
* Scikit-learn
* Git & GitHub

---

## 🎓 Academic Relevance

This project demonstrates:

* End-to-end **ETL pipeline design**
* Data cleaning and normalization
* Feature engineering for NLP
* Semantic search using embeddings
* Separation of data ingestion, storage, and serving layers
* Practical application of data engineering concepts

---

## 📜 Citation

Faculty data source:

> DA-IICT Faculty Directory
> [https://www.daiict.ac.in/faculty](https://www.daiict.ac.in/faculty)

---

## 👥 Contributors

* **Purav Shah** — 202518020
* **Jay Salot** — 202518029

---

## 📄 License

This project is intended for **academic use only**.

```

---

### ✅ What this README is good for
- ✔ College submission  
- ✔ Viva / evaluation  
- ✔ GitHub project review  
- ✔ Clear pipeline explanation  

If you want, I can:
- Shorten this for **exam PDF**
- Add **architecture diagram caption**
- Convert it into a **formal project report**
- Write **problem statement & conclusion**

Just tell me 👍
```
