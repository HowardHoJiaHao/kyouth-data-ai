import sqlite3
from pathlib import Path
import time

import ollama
import pandas as pd

def get_category(description):
    prompt = f"""Classify into exactly one category: Food, Transport, Utilities & Bill, 
    Study & Academic, Household & Cleaning, Selfcare & Health, Laundry, 
    Entertainment & Treat, Others. 
    Description: '{description}'. Return ONLY the category name."""
    
    try:
        response = ollama.chat(model='gemma2:2b', messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content'].strip()
    except Exception:
        return "Others"

# 1. Connect and read
db_path = Path(__file__).resolve().parent.parent / "expenses.db"
conn = sqlite3.connect(db_path)
# Read the table into a DataFrame
df = pd.read_sql('SELECT * FROM spending', conn)
conn.close()

# Ensure 'category' column exists
if 'category' not in df.columns:
    df['category'] = None

# 2. Process row-by-row
total_rows = len(df)
for index, row in df.iterrows():
    # Only process if category is missing or empty
    if pd.isna(row['category']) or row['category'] == "":
        print(f"Categorizing row {index + 1}/{total_rows}: {row['description']}...")
        
        # Get category
        category = get_category(row['description'])
        
        # Update DataFrame
        df.at[index, 'category'] = category
        
        # 3. Update the specific row in SQLite immediately
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE spending 
            SET category = ? 
            WHERE id = ?
        ''', (category, row['id']))
        conn.commit()
        conn.close()
        
        time.sleep(0.5) # Pause to keep the AI model stable

print("Successfully processed all rows with individual row saves.")