import sqlite3
from pathlib import Path

def run_data_profile(db_path):
    if not Path(db_path).exists():
        print(f"❌ Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    total = c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    nulls = c.execute("SELECT SUM(job_title IS NULL), SUM(company IS NULL), SUM(description IS NULL) FROM jobs").fetchone()
    avg_len = c.execute("SELECT AVG(LENGTH(description)) FROM jobs").fetchone()[0]
    short = c.execute("SELECT LENGTH(description), source_id, job_title FROM jobs ORDER BY LENGTH(description) ASC LIMIT 1").fetchone()
    long = c.execute("SELECT LENGTH(description), source_id, job_title FROM jobs ORDER BY LENGTH(description) DESC LIMIT 1").fetchone()

    print("--- 🔍 DATA QUALITY REPORT ---")
    print(f"📈 Total Records: {total}")
    print(f"❓ Missing Values -> job_title: {nulls[0] or 0}, company: {nulls[1] or 0}, description: {nulls[2] or 0}")
    print(f"📝 Avg Description Length: {int(avg_len or 0)} chars")
    print(f"⚠️ Shortest Description: {short[0]} chars\n   ↳ source_id: {short[1]} | job_title: {short[2]}")
    print(f"🚨 Longest Description: {long[0]} chars\n   ↳ source_id: {long[1]} | job_title: {long[2]}")
    conn.close()