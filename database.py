# database.py
import psycopg2
import pandas as pd
from config import POSTGRES_CONFIG

def get_schema():
    """Fetch schema metadata from PostgreSQL"""
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    query = """
    SELECT
        table_name,
        column_name,
        data_type,
        is_nullable
    FROM
        information_schema.columns
    WHERE
        table_schema = 'public'
    ORDER BY
        table_name, ordinal_position;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Format schema for LLM
    schema_str = "Database Schema:\n"
    for table in df['table_name'].unique():
        cols = df[df['table_name'] == table]
        schema_str += f"- Table: {table}\n  Columns: "
        schema_str += ", ".join([f"{row['column_name']} ({row['data_type']})" for _, row in cols.iterrows()])
        schema_str += "\n"
    return schema_str

def execute_sql(sql_query):
    """Run SQL and return result as DataFrame"""
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    try:
        df = pd.read_sql(sql_query, conn)
        return df
    finally:
        conn.close()