import os
import psycopg2
import base64
import pyarrow.parquet as pq
import pandas as pd
import json
from io import StringIO

# Database connection details from environment
conn = psycopg2.connect(
    host=os.getenv("MY_DB_HOST"),
    port=os.getenv("MY_DB_PORT"),
    user=os.getenv("MY_DB_USER"),
    password=os.getenv("MY_DB_PASSWORD"),
    dbname=os.getenv("MY_DB_NAME"),
    sslmode=os.getenv("MY_DB_SSLMODE", "require")
)

cur = conn.cursor()

# Query to fetch all rows from graphrag_outputs
cur.execute("SELECT file_path, content, file_type, source_dir FROM graphrag_outputs")
rows = cur.fetchall()

# Function to write content to file
def write_content(file_path, content, file_type):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if file_type == 'json':
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json.loads(content), f, indent=4)
    elif file_type in ['txt', 'graphml']:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    elif file_type == 'parquet':
        df = pd.read_json(StringIO(content), orient='split')
        df.to_parquet(file_path, index=False)
    elif file_type == 'binary':
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(content))


# Process each row and write content to file
for row in rows:
    file_path = os.path.join('/app/graphrag-folder/restore', row[0])
    content = row[1]
    file_type = row[2]
    write_content(file_path, content, file_type)

cur.close()
conn.close()

print("All files have been reconstructed from Azure-hosted PostgreSQL to /app/graphrag-folder/restore.")
