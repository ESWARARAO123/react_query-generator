# database.py
import psycopg2
import pandas as pd
from config import POSTGRES_CONFIG

def get_schema():
    """Fetch schema metadata from PostgreSQL"""
    try:
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
            table_name, 
            ordinal_position;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        if df.empty:
            return "No tables found in the database."
        
        # Format schema for LLM
        schema_str = "Database Schema:\n"
        for table in df['table_name'].unique():
            cols = df[df['table_name'] == table]
            schema_str += f"- Table: {table}\n  Columns: "
            schema_str += ", ".join([f"{row['column_name']} ({row['data_type']})" for _, row in cols.iterrows()])
            schema_str += "\n"
        return schema_str
    except psycopg2.OperationalError as e:
        error_msg = f"Database connection error: {str(e)}"
        print(error_msg)
        return f"Error: Could not connect to database. Please check if PostgreSQL is running and accessible at {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}"
    except Exception as e:
        error_msg = f"Error fetching schema: {str(e)}"
        print(error_msg)
        return f"Error: {error_msg}"

def execute_sql(sql_query):
    """Run SQL and return result as DataFrame"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        df = pd.read_sql(sql_query, conn)
        return df
    except Exception as e:
        print(f"Query execution error: {str(e)}")
        raise Exception(f"Failed to execute query: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print(get_schema())