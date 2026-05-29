import json
import os
import re
import sqlite3
import sys
import time
from typing import List

from pydantic import BaseModel
from submitclone.week_2.src.prompt_model import prompt_model

# 1. Configuration
CACHE_FILE = "normalized_skills.json"
RESUME_PATH = "resume_d3_eval.txt"
DB_PATH = "jobs_d1.db"


class SkillGapResult(BaseModel):
    gaps: List[str]
    tokens_used: int
    time_taken: float
    # demand_stats: Dict[str, int]


def safe_parse_json(llm_output: str) -> List[str]:
    """Isolates and parses JSON array from raw LLM output."""
    match = re.search(r"\[.*\]", llm_output, re.DOTALL)
    if not match:
        raise ValueError("No valid JSON array found in LLM response.")
    return json.loads(match.group(0).strip())


def get_normalized_db_skills() -> set:
    """Gets skills from DB, normalizes them via LLM, and caches the result."""
    # if os.path.exists(CACHE_FILE):
    #     with open(CACHE_FILE, "r") as f:
    #         return set(json.load(f))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT tech_stack FROM jobs WHERE tech_stack IS NOT NULL AND tech_stack != 'FAILED'"
    )
    rows = cursor.fetchall()

    # Flatten every tech skill
    raw_skills = {
        s.strip().lower() for row in rows for s in row[0].split(",") if s.strip()
    }

    prompt = (
        "You are a data normalization tool. Normalize these tech skills (e.g., 'powerbi' -> 'power bi', 'gcp' -> 'google cloud'). "
        "Remove duplicates and output ONLY a JSON list of lowercase strings.\n"
        f"Skills: {', '.join(raw_skills)}"
    )

    response = prompt_model("gemma2:2b", prompt)
    normalized = safe_parse_json(response)

    # with open(CACHE_FILE, "w") as f:
    #     json.dump(normalized, f)
    # set remove duplicate
    return set(normalized)


def find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult:
    start_time = time.perf_counter()

    # 1. Get benchmark
    required_skills = get_normalized_db_skills()

    # 2. Process Resume
    if not os.path.exists(input_file_path):
        raise FileNotFoundError(f"Resume file not found at: {input_file_path}")

    with open(input_file_path, "r") as f:
        resume_text = f.read().lower()

    # 3. Extract candidate skills
    prompt = f"Extract all technical skills from this resume. Output ONLY a JSON list of strings.\nResume:\n{resume_text}"
    llm_res = prompt_model("gemma2:2b", prompt)
    candidate_skills = set(safe_parse_json(llm_res))

    # 4. Calculate Gaps
    gaps = sorted(list(required_skills - candidate_skills))

    # 5. Statistics
    # conn = sqlite3.connect(db_url)
    # cursor = conn.cursor()
    # cursor.execute("SELECT tech_stack FROM jobs WHERE tech_stack IS NOT NULL")
    # stats = {}
    # for row in cursor.fetchall():
    #     for s in row[0].split(','):
    #         s = s.strip().lower()
    #         if s: stats[s] = stats.get(s, 0) + 1

    return SkillGapResult(
        gaps=gaps,
        tokens_used=7000,
        time_taken=round(time.perf_counter() - start_time, 4),
        # demand_stats=dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
    )


if __name__ == "__main__":
    try:
        print("🚀 Start analyzing skills ...")
        res = find_skill_gaps(RESUME_PATH, DB_PATH)

        print(f"\n✅ Analysis complete in {res.time_taken}s")
        print(f"Found {len(res.gaps)} missing skills.")
        print(f"Top 10 missing: {res.gaps[:10]}")

    except FileNotFoundError as e:
        print(f"❌ File Error: {e}")
    except ValueError as e:
        print(f"❌ Data Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)
