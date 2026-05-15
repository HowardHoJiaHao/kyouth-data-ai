# Job Data ETL Pipeline

## 📌 Project Description
The goal of this project is to automate the extraction of job listing data from raw, unstructured `.mhtml` and `.html` files (**Bronze**), transform them into structured, validated JSON formats (**Silver**), and finally load them into a queryable SQLite database (**Gold**).

## ⚙️ Setup Instructions

### Prerequisites 
*   **Python Version:** 3.14.2
*   **Package Manager:** `uv`

### Installation
After cloning the repository, install `uv` with the following command:

**macOS/Linux:**
```bash curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh ```

**Windows:**
```powershell -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex" ```

### Usage & Execution
## 🚀 Usage

### 🥉 Bronze: Ingestion
**Command:** `uv run python ingest`  
The Bronze Layer acts as the initial entry point of the ETL pipeline, specializing in the ingestion and normalization of raw MHTML (MIME HTML) files by moving data from the `0_source` directory to the `1_bronze` output folder. Because MHTML archives bundle a webpage's text, styles, and images into a single file—much like a digital email—this module uses the `email` library to traverse the multipart structure and the `quopri` library to decode Quoted-Printable characters, ensuring symbols and special formatting are preserved. By isolating the core `text/html` payload from these source archives and saving them as clean, UTF-8 encoded files in the bronze destination, the module provides an idempotent, resilient foundation that transforms messy snapshots into a standardized format ready for downstream processing.

### 🥈 Silver: Processing
**Command:** `uv run main.py process`  
The Silver Layer handles data refinement by transforming raw HTML files from the `1_bronze` directory into structured JSON documents within the `2_silver` folder. This stage focuses on parsing and extraction, using libraries like Beautiful Soup to strip away boilerplate code and isolate critical job data such as titles, salaries, and descriptions. By cleaning the text and organizing it into a consistent schema, this module converts unstructured web content into high-quality, "truthful" data ready for analytical use.

### 🥇 Gold: Loading
**Command:** `uv run main.py load`  
The Gold Layer represents the final curation stage, where structured JSON data is moved from the `2_silver` directory and loaded into the `3_gold` destination as a unified SQLite database (`jobs.db`). This module focuses on data persistence and schema enforcement, ensuring that all individual job records are aggregated into a queryable relational format. By consolidating the data into a single database file, it provides a performant, "production-ready" source for business intelligence and downstream reporting.

### 📊 Profiling: Quality Assurance
**Command:** `uv run main.py profile`  
The Profiling stage serves as the final validation step, targeting the `jobs.db` file located in the `3_gold` directory to generate a comprehensive data health report. This module analyzes the final dataset for null values, duplicates, and statistical distributions, ensuring the integrity of the information before it reaches the end user. By providing a snapshot of data quality, the profiler allows for quick identification of issues in the pipeline and ensures the final job data is both accurate and reliable.

### 🌊 Full Pipeline
**Command:** `uv run main.py all`  
The All command automates the entire end-to-end orchestration, executing the Bronze, Silver, Gold, and Profiling stages in sequence. This ensures a seamless flow of data from the raw `0_source` MHTML files all the way to the final, profiled `jobs.db` database. It is the primary command for production runs, guaranteeing that every transformation step is applied consistently to create a fresh, updated dataset.


## 🧠 Technical Reflections

### Module 1: The Extractor (Medallion & Lakehouses)
**Why is it useful to keep the original raw HTML files instead of directly inserting processed data into the database? What problems become easier to debug or recover from?**

*   **Answer:** Keeping original raw files acts as an immutable "source of truth" that protects against data loss. If a bug is discovered in the parsing logic or if business requirements change (e.g., needing to extract a new field like "Company Benefits" that was previously ignored), having the raw HTML allows for a complete re-processing of the historical data. Without these files, once data is transformed and the source is discarded, any uncaptured information is lost forever.
*   **Answer:** From a debugging perspective, raw files make it much easier to perform root-cause analysis. If the database contains garbled text or missing values, developers can trace the issue back to the specific source file to determine if the error originated from a malformed MHTML archive or a flaw in the extraction code. This decoupling of ingestion and transformation ensures that the pipeline is resilient and capable of full recovery without re-scraping the original websites.

### Module 2: Treatment Plant (ETL vs ELT & Scale)
**Why do cloud systems prefer loading raw data first before cleaning it (ELT)? What problems happen when processing files sequentially, and how does distributed processing help?**

*   **Answer:** Cloud systems prefer ELT because modern cloud data warehouses (like Snowflake or BigQuery) are designed to scale storage and compute independently, making it faster and cheaper to "dump" data first and use the warehouse's massive power to transform it later. This approach provides greater flexibility, as multiple different teams can apply different transformation logics to the same raw dataset simultaneously without needing to re-run the entire ingestion pipeline.
*   **Answer:** Sequential processing (one file at a time) creates a "bottleneck" where the total runtime grows linearly with the amount of data, making it impossible to handle millions of records efficiently. Distributed processing, like Apache Spark, solves this by splitting the workload across a cluster of machines. This allows the system to process thousands of files in parallel, drastically reducing the time from data arrival to business insight and ensuring the pipeline can handle "Big Data" volumes.

### Module 3: The Blueprint & The Vault (Storage & Contracts)
**What should happen if an important field like job_title disappears? Why fail early instead of silently inserting nulls into DB? How does INSERT OR IGNORE help prevent duplicate records?**

*   **Answer:** If a critical field like `job_title` disappears, the pipeline should trigger a validation error and halt the process for that record. Failing early is a "Data Contract" best practice that prevents "silent corruption," where dashboards and machine learning models produce incorrect results because they are consuming hidden null values. It is much easier to fix a broken pipeline than it is to clean up a "Gold" database filled with thousands of incomplete, low-quality records.
*   **Answer:** `INSERT OR IGNORE` acts as a safeguard for idempotency by checking for unique constraints (like a job ID or a URL hash) before writing. If the system attempts to load a job that already exists in the database, SQLite simply skips the operation instead of crashing or creating a duplicate. This ensures that even if the load command is run multiple times on the same data, the resulting "Gold" layer remains clean and consistent.

### Module 4: The QA Inspector & Orchestrator (Orchestration & DAGs)
**What happens if processor.py crashes halfway? How are automated orchestration tools more reliable than manual retries with Python scripts?**

*   **Answer:** If `processor.py` crashes halfway in a manual setup, the pipeline is left in an inconsistent "partial state," where some files are processed and others are not. Without an orchestrator, the user must manually figure out where the script stopped and restart it, which is prone to human error and duplicate processing.
*   **Answer:** Automated orchestration tools like Airflow are more reliable because they use a Directed Acyclic Graph (DAG) to track the state of every individual task. If a specific component fails, the orchestrator handles automatic retries, sends alerts to the engineering team, and ensures that downstream tasks (like load) never run on incomplete data. This provides "observability" and fault tolerance, allowing the pipeline to self-heal and run reliably 24/7 without manual intervention.
