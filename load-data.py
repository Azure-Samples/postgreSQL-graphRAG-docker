import psycopg2
import os

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

# Query all rows from the table
cur.execute("SELECT id, prompt_text FROM graphrag_inputs;")
rows = cur.fetchall()

# Output directory inside Docker container
output_dir = "/app/graphrag-folder/input"
os.makedirs(output_dir, exist_ok=True)

# Write each row to a .txt file
for row in rows:
    file_id = row[0]
    prompt_text = row[1]
    file_path = os.path.join(output_dir, f"input_{file_id}.txt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(prompt_text)

cur.close()
conn.close()
print("All rows saved as .txt files in /app/graphrag-folder/input.")
