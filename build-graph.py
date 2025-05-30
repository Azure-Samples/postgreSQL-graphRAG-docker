import psycopg2
import pyarrow.parquet as pq
import pandas as pd
import json
import os
import collections.abc

# Database connection details from environment
if os.getenv("USE_LOCAL_AGE") == "true":
    host = os.getenv("AGE_HOST")
    port = os.getenv("AGE_PORT")
    user = os.getenv("AGE_USER")
    password = os.getenv("AGE_PASSWORD")
    dbname = os.getenv("AGE_DB")
else:
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    dbname = os.getenv("POSTGRES_DB")

conn = psycopg2.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    dbname=dbname
)

cur = conn.cursor()

# Enable AGE and set search path
cur.execute("CREATE EXTENSION IF NOT EXISTS age;")
cur.execute("SET search_path = ag_catalog, \"$user\", public;")

# Drop the graph if it exists and recreate the graph
cur.execute("""
    SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'graphRAG';
""")
if cur.fetchone():
    cur.execute("SELECT drop_graph('graphRAG', true);")
    print("Existing graph 'graphRAG' dropped.")
else:
    print("Graph 'graphRAG' does not exist.")

cur.execute("SELECT create_graph('graphRAG');")
print("Graph 'graphRAG' will be created.")

# Escape function for safe Cypher strings
def escape_string(value):
    if isinstance(value, collections.abc.Iterable) and not isinstance(value, (str, bytes)):
        try:
            value = json.dumps(value)
        except Exception:
            value = str(value)
    if pd.isna(value):
        return ''
    return str(value).replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')

# Insert nodesdef insert_nodes(df, label):
def insert_nodes(df, label):
    for _, row in df.iterrows():
        props = ', '.join([f"{col}: '{escape_string(row[col])}'" for col in df.columns])

        # Use the correct column as name
        props = f"name: '{escape_string(row['title'])}', " + props

        cypher = f"CREATE (n:{label} {{{props}}})"
        cur.execute(f"SELECT * FROM cypher('graphRAG', $$ {cypher} $$) AS (n agtype);")
    print(f"Inserted {len(df)} rows into {label}")
    print(df.columns)


# Insert relationships 
def insert_relationships(df):
    for _, row in df.iterrows():
        source = escape_string(row['source'])
        target = escape_string(row['target'])

        rel_type = "RELATED_TO"

        # Build properties string excluding source and target
        props = ', '.join([
            f"{col}: '{escape_string(row[col])}'"
            for col in df.columns
        ])

        cypher = f"""
        MATCH (a), (b)
        WHERE a.name = '{source}' AND b.name = '{target}'
        CREATE (a)-[r:{rel_type} {{{props}}}]->(b)
        """

        try:
            cur.execute(f"SELECT * FROM cypher('graphRAG', $$ {cypher} $$) AS (r agtype);")
        except Exception as e:
            print(f"Error inserting relationship between {source} and {target}: {e}")
    print(f"Inserted {len(df)} rows into relationship")
    print(df.columns)


# Load and insert data
files = {
    "Document": "/app/graphrag-folder/output/documents.parquet",
    "Entity": "/app/graphrag-folder/output/entities.parquet",
    "Relationship": "/app/graphrag-folder/output/relationships.parquet"
}

for label, path in files.items():
    if os.path.exists(path):
        if path.endswith(".parquet"):
            df = pq.read_table(path).to_pandas()
        elif path.endswith(".json"):
            with open(path, 'r') as f:
                df = pd.json_normalize(json.load(f))
        if label == "Relationship":
            insert_relationships(df)
        else:
            insert_nodes(df, label)

conn.commit()
cur.close()
conn.close()
print("Data loaded into AGE graph successfully.")
