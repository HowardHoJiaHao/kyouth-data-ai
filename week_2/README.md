# Week 2: Intelligent Automation Pipeline

## 📌 Project Overview
The goal of this project is to build an automated, reliable data enrichment and analysis pipeline that processes job market demand data and evaluates candidate alignments. The system uses Large Language Models (LLMs) to perform structured, high-volume data classification and deterministic analytics across two main phases:

*   **Data Tagging:** Standardizing unstructured corporate job descriptions into clean, token-optimized technical stacks inside a local SQLite storage ecosystem.
*   **Skill Gap Analysis:** Parsing unstructured candidate resume text data and checking it against aggregated market demands to isolate missing technical competencies with mathematical determinism.

---

## ⚙️ Setup Instructions

### Prerequisites
*   **Operating System:** Linux or Windows Subsystem for Linux (WSL2 - Ubuntu 22.04 LTS or later)
*   **Python Version:** 3.10 or higher
*   **Package Manager:** `uv` (v0.1.0 or later)

### Installation
1.  **Clone the Repository:**
    
```
bash
    git clone <your-repository-url>
    cd week_2
```
2.  **Install `uv`:**
    
```
bash
    curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
    source $HOME/.local/bin/env
  ```
3.  **Sync Dependencies:**
    
```
bash
  uv sync
```

### Environment Configuration
The codebase accesses cloud services safely using system environment variables. 
1.  Open your configuration: `nano ~/.bashrc`
2.  Add the export line: `export GEMINI_API_KEY="your_actual_api_key_here"`
3.  Refresh your shell: `source ~/.bashrc`

---

## 🚀 Usage

### 1. Data Tagging Pipeline
Processes all database records lacking technical keywords.
*   **Command:** `uv run tag_data.py`
*   **Expected Output:**
    
```
text
    Analyzed Job 91397216: SQL, Python, Java, Spring Framework...
    Total tokens used: 14250, took 8412.311ms
```

### 2. Skill Gap Extraction
Evaluates candidate skill structures against the updated market database.
*   **Command:** `uv run find_skill_gaps.py`
*   **Expected Output:**
    
```
text
    📋 List of Missing Technical Competencies:
    • abap
    • enterprise systems
    • powerbi
```

---

## 🏗️ API / Function Reference

### Module: `tag_data.py`
*   **`tag_data(db_url: str) -> tuple[int, float]`**
    *   **Purpose:** Coordinates the database loop, reads untagged items, and commits batch edits.
    *   **Inputs:** `db_url` (Path to SQLite file).
    *   **Outputs:** `(total_tokens, total_time_ms)`.
*   **`extract_tech_stack_batch(client, jobs)`**
    *   **Purpose:** Packages list slices into XML blocks for multi-row LLM analysis.

### Module: `find_skill_gaps.py`
*   **`find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult`**
    *   **Purpose:** Reads resume, performs set-difference logic against DB, and returns structured results.
    *   **Inputs:** Path to resume file, database URL.
    *   **Outputs:** Pydantic object `SkillGapResult`.

---

## 💾 Data / Assumptions

### Data Architecture Flow
`[resume.txt]` → (LLM) → `[Resume Skills]` 
`[jobs_d1.db]` → (Batch) → `[Market Skills]`
`[Resume Skills]` ⊖ `[Market Skills]` → `[Sorted Gaps]`

### Database Schema
*   `id` (INTEGER, PK)
*   `description` (TEXT)
*   `tech_stack` (TEXT, Comma-separated)

### Assumptions
*   **Text Normalization:** Case-insensitivity and punctuation stripping are handled strictly to ensure identifier merging (e.g., "react.js" vs "ReactJS").
*   **Scope:** Only technical hard skills are tagged; soft skills or general management roles are excluded.

---

## 🧪 Testing
*   **Unit Testing:** Verified that logic skips already-tagged records.
*   **Determinism:** Executed `find_skill_gaps.py` 20 times with constant inputs to ensure identical output structures.
*   **Reproducibility:** Use the provided `jobs_d1.db` and `resume.txt` to verify the "Skill Gap" calculation.

---

## ⚠️ Limitations
*   **Performance:** Extremely long job descriptions may hit local prompt token thresholds due to the XML packing method.
*   **Accuracy:** String normalization is currently exact-match-based; semantic merging (synonym recognition) is limited.

---

## 🧠 Architecture Reflection

### Design Choices
*   **Modularity:** Separated DB I/O from LLM logic to allow for easy model swapping (e.g., Gemini Cloud vs. Ollama local).
*   **Data Integrity:** Used Pydantic for validation to ensure the "Skill Gap" output remains predictable for downstream systems.

### Trade-offs
*   **Batching Strategy:** Used small batch sizes (5 items). This sacrifices API efficiency (higher total request count) for lower memory consumption (ideal for 8GB RAM devices) and better checkpointing.

### Future Improvements
*   **Strict Pydantic Output:** Transitioning entirely to `genai` Structured Outputs would replace regex/split logic with native schema enforcement, eliminating parsing errors.