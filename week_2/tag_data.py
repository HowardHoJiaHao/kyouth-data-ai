import sqlite3
import time
import sys
import json
# Import your working router function directly from your previous script
from prompt_model import prompt_model

def tag_data(db_url: str):
    """
    Reads un-tagged job rows from SQLite, batches them, uses the chosen LLM 
    to extract technical stacks, and updates the database gracefully.
    If a batch fails validation, it logs the source_ids and skips them.
    """
    # 1. Establish database connection wrapped in exception handling
    try:
        conn = sqlite3.connect(db_url)
        cursor = conn.cursor()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    # 2. Assignment Configurations
    BATCH_SIZE = 3         # Keeping it small ensures local models don't lose track
    RETRY_DURATION = 5     # Seconds to wait before backing off on operational glitches
    batch_counter = 0
    model_choice: str = "gemma2:2b"
    
    print(f"🚀 Starting data tagging process using model nickname: [{model_choice}]")

    while True:
        try:
            # Fetch a batch of rows that DO NOT have a tech_stack value yet
            cursor.execute(
                "SELECT source_id, description FROM jobs WHERE tech_stack IS NULL OR tech_stack = '' LIMIT ?",
                (BATCH_SIZE,)
            )
            rows = cursor.fetchall()

            # If no rows remain, save changes and exit cleanly
            if not rows:
                print("\n✅ All rows have been processed successfully!")
                break

            current_batch_size = len(rows)
            
            # 3. Construct a clear, structured prompt asking for JSON
            # This is critical to guarantee we get back exactly 1 matching line per job id
            system_instructions = (
                "You are a precise data engineering parsing tool. Given a list of job descriptions, "
                "extract the core technical stack (programming languages, frameworks, databases, tools) "
                "as a comma-separated string for each. "
                f"You MUST return your output exactly as a JSON array containing exactly {current_batch_size} strings. "
                "Do not include Markdown syntax like ```json, headers, or conversational fluff.\n"
                "Example format: [\"Python, SQL, AWS\", \"Java, Spring Boot, Docker\"]\n\n"
            )
            # system_instructions = (
            #     "You are a precise data engineering tool. "
            #     "For the provided jobs, output ONLY a single valid JSON array of strings. "
            #     "The array must contain exactly one string per job. "
            #     "DO NOT output multiple arrays separated by commas. "
            #     "DO NOT output extra text. "
            #     "Example format: [\"Python, SQL\", \"Java, Spring Boot\"]\n"
            # )

            user_data = "Jobs to parse:\n"
            for idx, row in enumerate(rows):
                user_data += f"Job {idx}: {row[1]}\n---\n"

            full_prompt = system_instructions + user_data

            # 4. Invoke your custom model router function
            llm_response = prompt_model(model_choice, full_prompt)

            # 5. Robust structural matching & validation
            try:
                # Clean up any potential markdown code blocks the LLM might have wrapped around the JSON
                cleaned_json = llm_response.strip().lstrip("```json").rstrip("```").strip()
                tech_stacks_list = json.loads(cleaned_json)
                
                # Check if the number of strings matches our batch size exactly
                if len(tech_stacks_list) != current_batch_size:
                    raise ValueError("Mismatch between batch size and response count.")
                    
            except Exception as parse_error:
                print(f"\n⚠️ [Batch {batch_counter}] Parsing failed: {parse_error}")
                # ADD THIS LINE TEMPORARILY TO SEE THE RAW MANGLED DATA:
                print(f"🔍 Raw LLM Output was:\n{llm_response}")
                print("📋 Skipping the following rows to avoid infinite loops:")
                
                # Loop through the current batch rows to log their source_id and mark them skipped
                for row in rows:
                    failed_source_id = row[0]
                    print(f"Skipped Job {failed_source_id}")
                    
                    # Update database column so our next query passes over them
                    cursor.execute(
                        "UPDATE jobs SET tech_stack = '' WHERE source_id = ?",
                        (failed_source_id,)
                    )
                
                conn.commit()
                batch_counter += 1
                continue  # Jump directly to the next iteration to fetch fresh rows

            # 6. Success: Apply updates row-by-row and log to standard output
            for row, tech_stack in zip(rows, tech_stacks_list):
                job_id = row[0]
                
                # Clean up the output string slightly
                clean_stack = str(tech_stack).strip()
                
                cursor.execute(
                    "UPDATE jobs SET tech_stack = ? WHERE source_id = ?",
                    (clean_stack, job_id)
                )
                print(f"Analyzed Job {job_id}: {clean_stack}")

            # Commit changes to the database at the end of every successful batch
            conn.commit()
            batch_counter += 1

        except Exception as system_error:
            # Mandate: Handle all systemic errors gracefully without crashing or throwing stack traces
            print(f"🚨 An unexpected systemic error occurred: {str(system_error)}")
            time.sleep(RETRY_DURATION)
            continue

    # Clean up the database interface safely
    conn.close()

if __name__ == "__main__":
    # Points to your database file path relative to your current execution directory
    # Using cross-platform forward slashes to prevent escape character bugs
    target_db = "jobs_d1.db"
    
    # Run the processing routine
    tag_data(target_db)