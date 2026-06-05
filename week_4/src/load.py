import sqlite3
from pathlib import Path

import pandas as pd

# 1. Load and Clean the data
df = pd.read_csv(
    'data/howard_expenses.txt', 
    header=None, 
    names=['date', 'description', 'price'],
    on_bad_lines='skip',
    usecols=[0, 1, 2]
)
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df = df.dropna(subset=['price'])

# 2. Connect and define the table with an auto-incrementing ID
db_path = Path(__file__).resolve().parent.parent / "expenses.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop the old table if it exists so we can recreate it with an ID
cursor.execute('DROP TABLE IF EXISTS spending')

# Create the table with an AUTOINCREMENT ID
cursor.execute('''
    CREATE TABLE spending (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        description TEXT,
        price REAL,
        category TEXT
    )
''')

# 3. Insert the data
# We don't include 'id' here; SQLite fills it automatically
df.to_sql('spending', conn, if_exists='append', index=False)

conn.commit()
conn.close()

print(f"Success! {len(df)} rows imported with auto-incrementing IDs.")