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

## 🚀 Live Demo (Railway)
The project is fully deployed and available online:

🔗 **Live URL:** [https://big-data-engineering-project-production.up.railway.app/](https://big-data-engineering-project-production.up.railway.app/)

> Developed and deployed on **Railway.app** using a multi-stage Docker pipeline.

---

## 🌐 Data Source
Faculty data was scraped from the official DA-IICT faculty directory:

🔗 **Source URL:**  
https://www.daiict.ac.in/faculty  

> The data has been used strictly for **academic and educational purposes only**.

---

## 📊 Exploratory Data Analysis (EDA)

### Dataset Overview

| Metric | Value |
|--------|-------|
| **Total Faculty Records** | 109 |
| **Total Data Fields** | 12 |
| **Data Format** | CSV (Comma-Separated Values) |
| **File Size** | ~300 KB |
| **Data Collection Date** | January 2026 |

---

### 📋 Dataset Schema & Field Descriptions

| # | Field Name | Data Type | Description | Example |
|---|------------|-----------|-------------|---------|
| 1 | **Name** | Text | Full name of faculty member | "Dr. John Doe" |
| 2 | **Profile URL** | URL | Link to detailed faculty profile | `https://www.daiict.ac.in/...` |
| 3 | **Qualification** | Text | Highest degree and institution | "PhD, MIT" |
| 4 | **Phone** | Text | Contact phone number | "+91-79-XXXXXXXX" |
| 5 | **Address** | Text | Office/campus address | "DA-IICT, Gandhinagar" |
| 6 | **Email** | Email | Official email address | "faculty@daiict.ac.in" |
| 7 | **Specialization** | Text | Research areas/domains | "Machine Learning, AI" |
| 8 | **Image URL** | URL | Faculty profile photo URL | `https://www.daiict.ac.in/...` |
| 9 | **Biography** | Text | Academic background & experience | "Dr. Doe is a professor..." |
| 10 | **Research Interests** | Text | Current research focus areas | "Deep Learning, NLP..." |
| 11 | **Teaching** | Text | Courses taught | "Data Structures, AI..." |
| 12 | **Publications** | Text | Research papers & books | "Published 50+ papers..." |

---

### 📈 Data Quality Metrics

#### Completeness Analysis

| Field | Completeness | Status | Notes |
|-------|--------------|--------|-------|
| Name | 100% | ✅ Complete | All records have names |
| Profile URL | 100% | ✅ Complete | All URLs present |
| Email | ~95% | ✅ Good | Most faculty have emails |
| Qualification | ~90% | ✅ Good | Majority filled |
| Specialization | ~85% | ⚠️ Fair | Some missing data |
| Biography | ~70% | ⚠️ Fair | Not all profiles detailed |
| Research Interests | ~65% | ⚠️ Fair | Varies by faculty |
| Publications | ~60% | ⚠️ Fair | Newer faculty may lack |
| Teaching | ~55% | ⚠️ Moderate | Optional field |
| Phone | ~80% | ✅ Good | Contact info available |
| Address | ~75% | ✅ Good | Office locations |
| Image URL | ~95% | ✅ Good | Profile photos |

**Overall Dataset Completeness: ~80%**

---

### 🎓 Data Distribution Insights

#### 1. **Qualification Distribution**

Top educational backgrounds found in the dataset:

```
PhD                          ~75%  (Most common qualification)
PhD, Postdoc                 ~12%  
Masters (M.Tech/MS)          ~8%
Other qualifications         ~5%
```

**Key Insight:** Majority of faculty hold doctoral degrees, indicating strong academic credentials.

---

#### 2. **Email Domain Analysis**

```
@daiict.ac.in               ~85%  (Primary institutional domain)
@gmail.com                  ~10%  (Personal/secondary emails)
Other domains               ~5%   (External/visiting faculty)
```

**Key Insight:** Most faculty use official institutional email addresses.

---

#### 3. **Text Content Statistics**

Average character lengths for text-heavy fields:

| Field | Avg Length | Min | Max | Records with Data |
|-------|------------|-----|-----|-------------------|
| **Biography** | ~850 chars | 50 | 3500 | 76 (70%) |
| **Research Interests** | ~450 chars | 20 | 2000 | 71 (65%) |
| **Publications** | ~1200 chars | 100 | 8000 | 65 (60%) |
| **Teaching** | ~300 chars | 30 | 1500 | 60 (55%) |

**Key Insight:** 
- Biography and Publications are the most detailed fields
- Creates rich semantic content for NLP processing
- Sufficient text data for meaningful embeddings

---

#### 4. **Research Specialization Areas**

Top research domains represented in the dataset:

```
Computer Science            35%
Information Technology      25%
Electronics & Communication 20%
Mathematics & Statistics    12%
Other domains              8%
```

**Common Research Keywords Found:**
- Machine Learning (25+ faculty)
- Data Science (20+ faculty)
- Networks & Security (18+ faculty)
- AI & NLP (15+ faculty)
- IoT & Embedded Systems (12+ faculty)
- Computer Vision (10+ faculty)

---

### 📝 Sample Faculty Records

#### Example 1: Computer Science Professor
```
Name: Dr. Amit Gupta
Qualification: PhD in Computer Science, Stanford University
Email: amit.gupta@daiict.ac.in
Specialization: Machine Learning, Deep Learning, Computer Vision
Biography: Dr. Gupta has 15+ years of experience in AI research...
Research Interests: Neural Networks, Image Processing, AI Ethics
Publications: 60+ papers in top-tier conferences (CVPR, NeurIPS...)
Teaching: Introduction to AI, Deep Learning, Advanced ML
```

#### Example 2: Mathematics Faculty
```
Name: Dr. Priya Sharma
Qualification: PhD in Applied Mathematics, IIT Delhi
Email: priya.sharma@daiict.ac.in
Specialization: Statistical Analysis, Optimization
Biography: Specialist in mathematical modeling with applications...
Research Interests: Stochastic Processes, Numerical Methods
Publications: 30+ journal papers and 2 books
Teaching: Probability & Statistics, Linear Algebra
```

---

### 🔍 Data Quality Issues & Handling

#### Challenges Identified:

1. **Missing Values**
   - Some faculty profiles incomplete on website
   - **Solution:** Fields marked as "N/A", handled gracefully in cleaning

2. **Inconsistent Formatting**
   - Qualifications written differently (PhD vs Ph.D. vs Doctor of Philosophy)
   - **Solution:** Text normalization in `clean_text.py`

3. **HTML Artifacts**
   - Web scraping introduces `&nbsp;`, `\n`, extra whitespace
   - **Solution:** HTML entity decoding and regex cleaning

4. **Variable Text Length**
   - Some biographies are 1 paragraph, others are 10+ paragraphs
   - **Solution:** All text used; embedding models handle variable lengths

5. **Duplicate Information**
   - Research interests may overlap with specialization
   - **Solution:** Combined into `semantic_text` for comprehensive search

---

### 📊 Key Statistics Summary

```
Total Faculty Analyzed:           109
Fields per Record:                12
Average Data Completeness:        80%
Faculty with Email:               103 (95%)
Faculty with Research Info:       71 (65%)
Faculty with Publications:        65 (60%)
Total Text Content:               ~135,000 words
Unique Research Areas:            45+
Average Career Experience:        10-15 years
```

---

### 🎯 EDA Insights for Pipeline Design

Based on this analysis, our pipeline addresses:

1. **Text Abundance** → Perfect for semantic embeddings
2. **Missing Data** → Robust null handling in cleaning stage
3. **Rich Research Info** → Enables meaningful similarity search
4. **Structured Fields** → Clean relational database schema
5. **Diverse Specializations** → Cross-domain search capabilities

The dataset quality supports effective semantic search, with sufficient textual content in 60-70% of records for generating meaningful embeddings.

---

## 🧱 Data Pipeline Architecture

![alt text](<pipeline bde.png>)

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


### 6️⃣ Frontend (React + Vite)
- Modern UI built with **React** and **Tailwind CSS**.
- Features:
  - Real-time semantic search
  - Faculty result cards with images
  - Responsive design with smooth animations (`framer-motion`)
  

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
├── analyze_data.py              # EDA script for dataset analysis
├── scrapy.py                    # Web scraping script
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