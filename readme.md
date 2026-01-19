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
<img width="5764" height="838" alt="pipeline bde" src="https://github.com/user-attachments/assets/cbbb84aa-f006-4ce1-9571-6a01b14013bf" />

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

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-000000?style=flat-square)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-59666C?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![SentenceTransformers](https://img.shields.io/badge/SentenceTransformers-FF6F00?style=flat-square)
![Scikit--learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)


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



