import os
import json
import psycopg2
import base64
import pyarrow.parquet as pq
import pandas as pd
from datetime import datetime

# MY_DB connection
conn = psycopg2.connect(
    host=os.getenv("MY_DB_HOST"),
    port=os.getenv("MY_DB_PORT"),
    user=os.getenv("MY_DB_USER"),
    password=os.getenv("MY_DB_PASSWORD"),
    dbname=os.getenv("MY_DB_NAME"),
    sslmode=os.getenv("MY_DB_SSLMODE", "require")  # default to 'require' if not set
)
cur = conn.cursor()

# Create table if it doesn't exist
cur.execute("""
CREATE TABLE IF NOT EXISTS graphrag_outputs (
    file_path TEXT PRIMARY KEY,
    content TEXT,
    file_type TEXT,
    source_dir TEXT,
    created_at TIMESTAMP
)
""")
conn.commit()

# Function to insert file content into the table
def insert_file_content(file_path, content, file_type, source_dir):
    cur.execute("""
    INSERT INTO graphrag_outputs (file_path, content, file_type, source_dir, created_at)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (file_path) DO UPDATE SET
    content = EXCLUDED.content,
    file_type = EXCLUDED.file_type,
    source_dir = EXCLUDED.source_dir,
    created_at = EXCLUDED.created_at
    """, (file_path, content, file_type, source_dir, datetime.now()))
    conn.commit()

# Function to process files in a directory
def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            if file == 'context.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    if not f.read().strip():
                        continue
            if file.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        content = json.dumps(json.load(f))
                    except json.JSONDecodeError:
                        try:
                            f.seek(0)
                            lines = [json.loads(line) for line in f if line.strip()]
                            content = json.dumps(lines)
                        except json.JSONDecodeError:
                            print(f"Skipping JSON file: {file_path}")
                            continue
                insert_file_content(relative_path, content, 'json', directory)
            elif file.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                insert_file_content(relative_path, content, 'txt', directory)
            elif file.endswith('.graphml'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                insert_file_content(relative_path, content, 'graphml', directory)
            elif file.endswith('.parquet') or file.endswith('.arrow'):
                table = pq.read_table(file_path)
                content = table.to_pandas().to_json(orient='split')
                insert_file_content(relative_path, content, 'parquet', directory)
            elif file.endswith('.bin') or file.endswith('.npy'):
                with open(file_path, 'rb') as f:
                    content = base64.b64encode(f.read()).decode('utf-8')
                insert_file_content(relative_path, content, 'binary', directory)

# Directories to process
directories = [
    '/app/graphrag-folder/output',
    '/app/graphrag-folder/cache',
    '/app/graphrag-folder/prompts',
    '/app/graphrag-folder/logs',
    '/app/graphrag-folder/update_output'
]

# Process each directory
for directory in directories:
    process_directory(directory)

cur.close()
conn.close()
print("All relevant files have been processed and stored in PostgreSQL.")
