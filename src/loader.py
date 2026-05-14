import json, sqlite3
from pathlib import Path

def load_all_jsons(input_dir, output_dir):
    input_path, output_path = Path(input_dir), Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(output_path / "jobs.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            source_id TEXT PRIMARY KEY, job_title TEXT, company TEXT, description TEXT, tech_stack TEXT
        )
    """)

    json_files = list(input_path.glob("*.json"))
    total, inserted, skipped = len(json_files), 0, 0
    print("🥇 Gold:...")

    for file_path in json_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tech_stack = data.get("tech_stack")
        if isinstance(tech_stack, list):
            tech_stack = ", ".join(tech_stack)

        cursor.execute(
            """
            INSERT INTO jobs (source_id, job_title, company, description, tech_stack)
            VALUES (?,?,?,?,?)
            ON CONFLICT(source_id) DO UPDATE SET
                job_title = excluded.job_title,
                company = excluded.company,
                description = excluded.description,
                tech_stack = excluded.tech_stack
            """,
            (data["source_id"], data["job_title"], data["company"], data["description"], tech_stack),
        )
        
        if cursor.rowcount > 0:
            print(f"✅ Upserted: {file_path.name}")
            inserted += 1
        else:
            print(f"⏭️ Skipped: {file_path.name}")
            skipped += 1

    conn.commit()
    conn.close()
    print(f"\n📊 Gold Summary:\nTotal: {total} | Inserted: {inserted} | Skipped: {skipped}")