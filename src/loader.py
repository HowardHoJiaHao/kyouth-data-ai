import json
import sqlite3
from pathlib import Path

def load_all_jsons(input_dir, output_dir):
    # 1. PATH SETUP
    # Convert string paths to Path objects for easier cross-platform handling
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Ensure the output directory exists; creates it if it doesn't
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 2. DATABASE INITIALIZATION
    # Connect to (or create) the SQLite database file
    conn = sqlite3.connect(output_path / "jobs.db")
    cursor = conn.cursor()
    
    # Create the 'jobs' table. source_id is the unique PRIMARY KEY to prevent duplicates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            source_id TEXT PRIMARY KEY, 
            job_title TEXT, 
            company TEXT, 
            description TEXT, 
            tech_stack TEXT
        )
    """)

    # 3. FILE DISCOVERY
    # Find all files ending in .json in the input directory
    json_files = list(input_path.glob("*.json"))
    total = len(json_files)
    inserted = 0
    skipped = 0
    
    print(f"🥇 Starting Gold Load: Processing {total} files...")

    # 4. DATA PROCESSING LOOP
    for file_path in json_files:
        try:
            # Open and read the individual JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 5. THE UPSERT (INSERT OR UPDATE)
            # We use .get() for all fields so the script doesn't crash if a field is missing.
            # If source_id exists, we update the existing row with the newest data (Idempotency).
            cursor.execute(
                """
                INSERT INTO jobs (source_id, job_title, company, description, tech_stack)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(source_id) DO UPDATE SET
                    job_title = excluded.job_title,
                    company = excluded.company,
                    description = excluded.description,
                    tech_stack = excluded.tech_stack
                """,
                (
                    data.get("source_id"), 
                    data.get("job_title"), 
                    data.get("company"), 
                    data.get("description"), 
                    data.get("tech_stack"),
                ),
            )
            
            # cursor.rowcount tells us if a row was added/updated (>0) or remained unchanged (0)[cite: 3]
            if cursor.rowcount > 0:
                print(f"✅ Processed: {file_path.name}")
                inserted += 1
            else:
                print(f"⏭️ Skipped (no changes): {file_path.name}")
                skipped += 1

        except Exception as e:
            # If one file fails (e.g., corrupted JSON), we log it and keep going[cite: 3]
            print(f"❌ Error processing {file_path.name}: {e}")
            continue

    # 6. CLEANUP
    # Commit saves all changes permanently to the jobs.db file[cite: 3]
    conn.commit()
    conn.close()
        
    print(f"\n📊 Gold Summary:\nTotal: {total} | Inserted: {inserted} | Skipped: {skipped}")  # Final summary.
