Week 2: Intelligent Automation Pipeline
Project Overview
The goal of this project is to build an automated, reliable data enrichment and analysis pipeline that processes job market demand data and evaluates candidate alignments. The system uses local and cloud-based Large Language Models (LLMs) to perform structured, high-volume data classification and deterministic analytics across two main phases:

Data Tagging: Standardizing unstructured corporate job descriptions into clean, token-optimized technical stacks inside a local SQLite storage ecosystem.

Skill Gap Analysis: Parsing unstructured candidate resume text data and checking it against aggregated market demands to isolate missing technical competencies with mathematical determinism.

Setup Instructions
Prerequisites
Operating System: Linux or Windows Subsystem for Linux (WSL2 - Ubuntu 22.04 LTS or later)

Python Version: Python 3.10 or higher

Package Manager: uv (v0.1.0 or later) for rapid, isolated runtime dependency management

Environment Installation
Install the uv toolchain:
If uv is not present inside your WSL terminal layer, install it cleanly using the official Astral script:

Bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
Clone and Navigate to Workspace:

Bash
cd week_2
Verify Database and Resources:
Ensure the foundational project components are placed securely inside your workspace directory:

jobs_d1.db (SQLite source database asset)

resume.txt (Target profile for alignment analysis)

Configuring Environment Variables
The codebase accesses cloud services safely using system environment variables instead of hardcoding raw secret tokens into files.

Open your profile setup using a command-line editor:

Bash
nano ~/.bashrc
Scroll to the bottom of the file and export your Google AI Studio credentials:

Bash
export GEMINI_API_KEY="AIzaSyYourActualSecretKeyHere..."
Save and close (Ctrl + O, Enter, Ctrl + X), then refresh your active terminal shell configuration matrix:

Bash
source ~/.bashrc
Usage
The system leverages uv run to dynamically handle isolated environments, dependencies, and script invocations in single, clean commands.

1. Execute Data Tagging Pipeline
Processes all database records lacking technical keywords, dynamically logging parsed records to stdout.

Bash
uv run tag_data.py
Expected Output:

Plaintext
Analyzed Job 91397216: SQL, Python, Java, Spring Framework, R, Excel, Tableau
Analyzed Job 91347112: Java, Spring Boot, Python, PyTorch, TensorFlow, Git, CI/CD
...
Total tokens used: 14250, took 8412.311ms
2. Execute Skill Gap Extraction
Evaluates candidate skill structures against the updated market database, returning sorted gap matrices.

Bash
uv run find_skill_gaps.py
Expected Output:

Plaintext
=================================================================
🧠 RUNNING COGNITIVE EVALUATION PATHWAY: SKILL GAP METRICS
=================================================================

✅ Analysis Phase Sealed Successfully inside 1240.15ms
📊 Identified Total Skill Gaps: 3

📋 List of Missing Technical Competencies:
--------------------------------------------------
  • abap
  • enterprise systems
  • powerbi
--------------------------------------------------

✨ Validated Pydantic Object Output:
{
  "gaps": [
    "abap",
    "enterprise systems",
    "powerbi"
  ]
}
API / Function Reference
Module: tag_data.py
Manages token-optimized, batched data extraction to enrich missing database parameters.

tag_data(db_url: str) -> tuple[int, float]

Purpose: Coordinates the database loop, reads untagged items, executes processing calls, and commits batch edits.

Inputs: db_url (String path matching target SQLite database file)

Outputs: Returns a tuple containing (total_tokens_consumed, total_execution_time_ms).

extract_tech_stack_batch(client: genai.Client, jobs: list) -> tuple[dict, int, int]

Purpose: Packages list slices into unified XML structural blocks to run multi-row analysis in single API interactions.

Module: find_skill_gaps.py
Processes profile configurations and cross-checks capacity footprints with strict validation constraints.

find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult

Purpose: Coordinates file read and database lookup methods, runs mathematical difference evaluations, and generates a structured dataset.

Inputs: input_file_path (Path to source resume text file), db_url (Database file target link)

Outputs: A structured SkillGapResult Pydantic object instance.

Data / Assumptions
Data Architecture Flow
Plaintext
[resume.txt] ---------> (LLM Parsing) -----------> [Resume Skills Set]
                                                           |
                                                   (Set Difference) ---> [Sorted Lowercase Gaps]
                                                           |
[jobs_d1.db] ---------> (Batch Extraction) --------> [Market Skills Set]
Database Schema Matrix
The application references a jobs table matching the following layout:

id (INTEGER, Primary Key)

description (TEXT, Unstructured original job text)

tech_stack (TEXT, Comma-separated normalized keywords appended by pipeline execution)

Engineering Assumptions & Simplifications
Text Cleaning Rules: All strings are stripped of punctuation anomalies, lowercased, and whitespace-trimmed. This guarantees that "C++", "c++", and "C++ " merge uniformly to avoid duplicate reporting.

Filtering Focus: Non-technical credentials (such as leadership or management designations) and standard certifications are skipped to protect the purity of the technical stack analysis.

Testing
Test Scenarios
Empty Database States: Verified that passing a fully populated database cleanly prints "No data to tag", exiting safely without initiating network requests.

Missing Token Fallback: Simulated missing API usage metadata to verify that word splitting counts close approximations at 4 tokens per word.

Determinism Verification: Executed find_skill_gaps.py across 20 distinct consecutive runs. The output maintained zero sorting variances and identical value structures, proving total algorithmic determinism.

Limitations
Context Token Drift: The script leverages an XML micro-packing method (<job id="x">) to maximize context windows. Extremely long job descriptions can cause batch sizes to push up against local prompt thresholds.

Semantic Merging Deficiencies: The current string normalization structure checks exact string values. For instance, "react.js" and "reactjs" may register as two separate entities rather than merging into a single technology stack record.

Architecture Reflection
Design Choices
Modularity and separation of concerns were heavily prioritized during development. Database input/output methods are kept entirely separate from model interaction functions. This clean decoupling makes switching out execution parameters incredibly simple, as seen when moving between Google's cloud-based gemini-2.5-flash-lite model and local instances running via Ollama network sockets.

Applied Trade-offs
Batch Slices vs. Payload Latency: A small, justifiable batch boundary of 5 items was selected. While larger batches reduce overall API transaction count, smaller chunks protect system RAM allocations on 8 GB memory devices and provide clear, resilient log tracking checkpoints if a network dropout occurs.

Cloud Processing vs. Local Speed: Cloud endpoints were selected over local processing paths for production deployment. This satisfies the strict requirement to use Gemini models exclusively while delivering fast processing speeds and precise token metrics.

Future Improvements
Given more development time, the pipeline's intelligence could be enhanced by introducing Strict Pydantic Structured Outputs natively into the tag_data generation configurations. Forcing the model to respond using JSON schemas completely removes the need for manual text split rules and regex patterns, guaranteeing a bulletproof, crash-resistant extraction process.