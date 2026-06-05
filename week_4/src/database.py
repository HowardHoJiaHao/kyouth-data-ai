import sqlite3
import ollama
import pandas as pd
from datetime import datetime

DB_PATH = "expenses.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spending (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            price REAL,
            category TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_category_from_ai(description):
    prompt = f"""Classify this into exactly one category: Food, Transport, Utilities & Bill, 
    Study & Academic, Household & Cleaning, Selfcare & Health, Laundry, 
    Entertainment & Treat, Others. Description: '{description}'. Return ONLY the category name."""
    
    try:
        response = ollama.chat(model='deepseek-r1:1.5b', messages=[{'role': 'user', 'content': prompt}])
        content = response['message']['content']
        # Strip thinking process
        if "<think>" in content:
            content = content.split("</think>")[-1]
        return content.strip().replace("'", "").replace('"', "")
    except Exception:
        return "Others"

def add_expense_to_db(description, price):
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    category = get_category_from_ai(description)
    cursor.execute(
        'INSERT INTO spending (date, description, price, category) VALUES (?, ?, ?, ?)',
        (today, description, price, category)
    )
    conn.commit()
    conn.close()

def get_all_expenses():
    conn = get_connection()
    try:
        return pd.read_sql('SELECT * FROM spending', conn)
    finally:
        conn.close()

def execute_natural_language_query(sql_query):
    # Security: Prevent destructive commands
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE"]
    if any(word in sql_query.upper() for word in forbidden):
        return "Error: Unauthorized query detected."
    
    conn = get_connection()
    try:
        return pd.read_sql(sql_query, conn)
    except Exception as e:
        return f"Database error: {e}"
    finally:
        conn.close()

# Initialize upon import
initialize_db()