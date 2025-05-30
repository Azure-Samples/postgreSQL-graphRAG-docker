import psycopg2
import os
from dotenv import load_dotenv

# PostgreSQL connection
load_dotenv()
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    dbname=os.getenv("POSTGRES_DB")
)
cur = conn.cursor()

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PostgreSQL connection
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    dbname=os.getenv("POSTGRES_DB"),
    sslmode='require'  # Required for Azure PostgreSQL
)
cur = conn.cursor()

# Create the table if it doesn't exist
cur.execute("""
CREATE TABLE IF NOT EXISTS graphrag_inputs (
    id SERIAL PRIMARY KEY,
    prompt_text TEXT NOT NULL
);
""")
conn.commit()

# Directory containing your .txt files
input_dir = "C:/Users/helenzeng/graphRAG2/postgreSQL-AGE/data/input"

# Insert each .txt file's content into the table
for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(input_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            cur.execute("INSERT INTO graphrag_inputs (prompt_text) VALUES (%s);", (content,))
            conn.commit()

        # Print file name and line count
        print(f"Processed file: {filename}")
        print(f"Number of lines in {filename}: {len(content.splitlines())}")

cur.close()
conn.close()
print("All .txt files inserted into PostgreSQL.")
