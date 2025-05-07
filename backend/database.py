# database.py
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from config import DB_CONFIG

def get_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )
        return conn
    except Exception as e:
        raise Exception(f"Failed to connect to database: {str(e)}")

def execute_sql(query):
    """Execute SQL query and return results as pandas DataFrame"""
    try:
        conn = get_connection()
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        raise Exception(f"Failed to execute query: {str(e)}")

def get_schema():
    """Get database schema information"""
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        schema = {}
        for table in tables:
            table_name = table['table_name']
            
            # Get columns for each table
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            schema[table_name] = {
                'columns': [col['column_name'] for col in columns],
                'types': {col['column_name']: col['data_type'] for col in columns},
                'nullable': {col['column_name']: col['is_nullable'] == 'YES' for col in columns}
            }
        
        cursor.close()
        conn.close()
        return schema
    except Exception as e:
        raise Exception(f"Failed to get schema: {str(e)}")

def get_tables():
    """Get list of all tables in the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        return tables
    except Exception as e:
        raise Exception(f"Failed to get tables: {str(e)}")

if __name__ == "__main__":
    print(get_schema())