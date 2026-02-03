# LLM Conversation Log

This document contains the prompts asked by the user and the corresponding answers provided during this chat. It is intended for long-term reference, reproducibility, and reuse in data engineering and system design contexts.

---

## Prompt 1: Designing a Faculty Data Ingestion Pipeline

**User Prompt**

> I am building a data ingestion pipeline for a college faculty directory.
> My goal is not just to scrape HTML, but to extract structured academic data
> that will be stored in a relational database.
> Before writing code, explain:
> - How you would navigate a faculty directory with pagination or profile links
> - What information should be treated as mandatory vs optional
> - How you would handle broken pages, missing sections, or partial profile
> Answer from a data engineering perspective, not a web scraping tutorial.

**Assistant Answer**

From a data engineering perspective, the core problem is not scraping HTML, but reliably acquiring, validating, and persisting academic entity data from a semi-structured and unstable upstream source.

The pipeline should be designed around two phases: entity discovery and entity enrichment. Discovery focuses on coverage—collecting faculty identifiers such as name, profile URL, and department from paginated index pages. Enrichment focuses on completeness—extracting detailed attributes from individual profile pages. These two phases must be decoupled so enrichment failures do not erase discovered entities.

Mandatory fields are those required for identity and referential integrity, such as faculty name, unique identifier (profile URL or hash), department, source system, and ingestion timestamp. Optional fields include designation, contact details, qualifications, research interests, publications, and external links. Optional does not mean unimportant; it means non-blocking.

Broken pages and missing sections are expected conditions, not exceptions. The system should mark enrichment attempts with explicit status flags, log failures, retry deterministically, and never delete existing entities due to enrichment errors. Partial profiles should be stored as-is, with NULLs where data is missing, avoiding inference or guessing.

The guiding principles are separation of concerns, schema-first design, failure tolerance, idempotency, and observability.

---

## Prompt 2: Text Cleaning Strategy for Faculty Data

**User Prompt**

> I have scraped faculty profile data from HTML pages.
> The text contains:
> - HTML entities
> - Irregular spacing
> - Non-ASCII characters
> - Missing values such as "N/A" or empty sections
> Design a text cleaning strategy that prepares this data for long-term storage
> and downstream analytics.
> Explain:
> - What should be cleaned
> - What should NOT be aggressively cleaned
> - How to handle null or malformed values safely
> Do not assume this data will only be used once.

**Assistant Answer**

A robust cleaning strategy must distinguish between cleaning, normalization, and interpretation. Only cleaning and limited normalization belong in the ingestion pipeline.

What should be cleaned includes HTML entities, tags, encoding artifacts, irregular whitespace, invisible control characters, and placeholder values such as "N/A" or "-". These elements have no semantic meaning and should be removed or normalized deterministically. Unicode should be normalized, but non-ASCII characters must be preserved.

What should not be aggressively cleaned includes academic semantics: punctuation, symbols, degree formats, multilingual text, diacritics, and structural meaning. Removing or simplifying these destroys information and harms future reuse.

Null handling must be explicit. Placeholder values and empty fields should be stored as true NULLs. The pipeline should distinguish between missing data, empty data, and parsing failures using flags or metadata. When possible, raw extracted text should be preserved alongside cleaned text to allow reprocessing and auditing.

The recommended architecture is layered: raw ingestion, canonical cleaning, and analytical views. Cleaning must be deterministic, versioned, and logged to ensure reproducibility.

---

## Prompt 3: Persisting Cleaned CSV Data into SQLite

**User Prompt**

> I already have a cleaned CSV file containing faculty data.
> I want to persist this data in SQLite using a predefined schema.
> Explain:
> - How schema.sql should be used in the loading process
> - Why the schema should be created before inserting data
> - How to safely insert CSV rows into SQLite without breaking the schema
> Focus on correctness, persistence, and reproducibility.

**Assistant Answer**

The schema.sql file is the authoritative contract defining how data must exist in storage. It defines tables, columns, types, and constraints and must be executed before any data is inserted. It should be version-controlled and treated as a first-class artifact.

Creating the schema before loading data ensures constraints are enforced at write time, prevents implicit or incorrect table creation, and guarantees deterministic, repeatable loads. Without a predefined schema, SQLite may silently accept incorrect types or malformed data.

CSV rows should be validated before insertion, inserted using parameterized queries, and written inside explicit transactions to guarantee atomicity. Constraint violations must be handled explicitly by aborting, skipping with logs, or quarantining rows. Identity fields should be stable and independent of human-readable names.

The same CSV, schema.sql, and loading logic must always produce the same database state. Schema evolution should be explicit and never inferred from CSV changes.

---

## Prompt 4: Exposing Faculty Data via FastAPI

**User Prompt**

> I want to expose my stored faculty data through a FastAPI service.
> The API should support:
> 1) Fetching all faculty records
> 2) Fetching a single faculty by ID
> Explain:
> - Why these two endpoints are sufficient for a first version
> - How FastAPI should interact with SQLite safely
> - What kind of response structure is appropriate for downstream users
> Assume this API will be used by data scientists, not end users.

**Assistant Answer**

These two endpoints cover the fundamental access patterns: bulk reads for dataset-level analysis and entity reads for inspection and validation. Additional filters and search endpoints add complexity without increasing core capability and can be layered later.

FastAPI should interact with SQLite using request-scoped connections, parameterized queries, and read-only access patterns. SQLite is well-suited for deterministic, read-heavy workloads if connections are not shared globally. Errors such as missing records or schema mismatches should fail loudly and explicitly.

Response structures should be flat, predictable JSON objects that map directly to the relational schema. Fields should always be present, with explicit NULL values rather than missing keys. Bulk endpoints should include lightweight metadata such as record counts. The API should be versioned early and treated as a long-term data contract rather than a UI backend.

---

## End of Document

This file captures the conceptual design decisions and reasoning discussed in this conversation, intended for reuse in data engineering documentation and LLM-assisted workflows.
