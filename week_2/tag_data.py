import sqlite3
import json
import re
# Import your working router function directly from your previous script
from prompt_model import prompt_model

def tag_data(db_url: str):
    """
    Reads un-tagged job rows from SQLite, batches them, uses the chosen LLM 
    to extract technical stacks, and updates the database gracefully.
    If a batch fails validation, it marks them as 'FAILED' to skip them.
    """
    # 1. Establish database connection
    try:
        conn = sqlite3.connect(db_url)
        cursor = conn.cursor()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    # 2. Assignment Configurations
    BATCH_SIZE = 3
    model_choice: str = "gemma2:2b"
    
    print(f"🚀 Starting data tagging process using model nickname: [{model_choice}]")

    while True:
        # Fetch a batch of rows that DO NOT have a tech_stack value yet
        # Added 'AND tech_stack != 'FAILED'' to prevent infinite loops
        cursor.execute(
            """
            SELECT source_id, description FROM jobs 
            WHERE (tech_stack IS NULL OR tech_stack = '') 
            AND tech_stack != 'FAILED' 
            LIMIT ?
            """,
            (BATCH_SIZE,)
        )
        rows = cursor.fetchall()

        # If no rows remain, save changes and exit cleanly
        if not rows:
            print("\n✅ All rows have been processed successfully!")
            break

        current_batch_size = len(rows)
        
        # 3. Construct a clear, structured prompt
        system_instructions = (
            "You are a professional technical data extraction engine. Your task is to process a batch of job descriptions "
            "and extract the core technical stack for each, normalized to a comma-separated string of keywords.\n\n"
            
            "GUIDELINES:\n"
            "1. SCOPE: Extract a comprehensive stack, including:\n"
            "   - Cloud: AWS, Google Cloud, Alibaba Cloud, etc.\n"
            "   - Backend/API: Node.js, Spring Boot, PHP, RESTful API design.\n"
            "   - Infrastructure/DevOps: Docker, Nginx, Prometheus, Grafana, GitHub Actions, Linux.\n"
            "   - Data/AI: LLM, RAG, MongoDB, MySQL, Power BI, Excel, Data processing, Feature engineering.\n"
            "2. FORMAT: You MUST return a valid JSON array of strings.\n"
            f"3. LENGTH: You must return EXACTLY {current_batch_size} strings, one for each job description provided in the input order.\n"
            "4. CLEANLINESS: Return ONLY the JSON array. Do not include Markdown blocks (```json), "
            "no conversational text, no explanations, no job IDs, and no headers.\n\n"
            
            "Example of the exact expected output format:\n"
            "[\"Node.js, AWS, MongoDB\", \"Java, Spring Boot, Docker, Grafana\", \"PHP, MySQL, Linux development environments\"]"
        )

        user_data = "Jobs to parse:\n"
        for idx, row in enumerate(rows):
            user_data += f"Job {idx}: {row[1]}\n---\n"

        full_prompt = system_instructions + user_data

        # 4. Invoke your custom model router function
        llm_response = prompt_model(model_choice, full_prompt)

        # 5. Robust structural matching & validation
        tech_stacks_list = None 
        try:
            # # Clean up any potential markdown code blocks
            # cleaned_json = llm_response.strip().lstrip("```json").rstrip("```").strip()
            # tech_stacks_list = json.loads(cleaned_json)
            
            # if len(tech_stacks_list) != current_batch_size:
            #     raise ValueError("Mismatch between batch size and response count.")
                # 1. Regex to isolate the first valid-looking JSON array, ignoring all other text
            # This captures everything between the first '[' and last ']'
            match = re.search(r'\[.*\]', llm_response, re.DOTALL)
            # It effectively "cuts out" the JSON and throws the conversational filler
            
            if not match:
                raise ValueError("No JSON array found in LLM response.")
            
            cleaned_json = match.group(0).strip()
            
            # 2. Parse the isolated string
            # turn it into list
            tech_stacks_list = json.loads(cleaned_json)
            # Example
            # tech_stacks_list = [
            #     "Node.js, AWS",        # Index 0 (corresponds to Job 0)
            #     "Java, Spring Boot",   # Index 1 (corresponds to Job 1)
            #     "PHP, MySQL"           # Index 2 (corresponds to Job 2)
            # ]
            
            # 3. Structural validation
            if not isinstance(tech_stacks_list, list):
                raise ValueError("Response is not a list.")
                
            if len(tech_stacks_list) != current_batch_size:
                # Log this mismatch instead of just crashing if you want to keep running
                print(f"Mismatch: Expected {current_batch_size}, got {len(tech_stacks_list)}")
                raise ValueError("Mismatch between batch size and response count.")
        except Exception as parse_error:
            print(f"\n⚠️ Parsing failed: {parse_error}")
            print(f"🔍 Raw LLM Output was:\n{llm_response}")
            
            # Mark failed rows as 'FAILED' to skip them in future loops
            for row in rows:
                cursor.execute(
                    "UPDATE jobs SET tech_stack = 'FAILED' WHERE source_id = ?",
                    (row[0],)
                )
            conn.commit()
            continue # Jump to the next batch

        # 6. Success: Apply updates row-by-row
        # zip pairing them up
        for row, tech_stack in zip(rows, tech_stacks_list):
            job_id = row[0]
            clean_stack = str(tech_stack).strip()
            # By default, .strip() removes:, Spaces (" "), Tabs (\t), Newlines (\n), Carriage returns (\r)
            cursor.execute(
                "UPDATE jobs SET tech_stack = ? WHERE source_id = ?",
                (clean_stack, job_id)
            )
            print(f"Analyzed Job {job_id}: {clean_stack}")

        conn.commit()

    # Clean up the database interface safely
    conn.close()

if __name__ == "__main__":
    target_db = "jobs_d1.db"
    tag_data(target_db)