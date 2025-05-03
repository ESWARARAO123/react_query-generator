# database.py
import psycopg2
import pandas as pd
from config import POSTGRES_CONFIG

def get_schema():
    """Fetch schema metadata from PostgreSQL"""
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def execute_sql(sql_query):
    """Run SQL and return result as DataFrame"""
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    try:
        df = pd.read_sql(sql_query, conn)
        return df
    finally:
        conn.close()

if __name__ == "__main__":
    print(get_schema())