import os
import pandas as pd
import psycopg2
from psycopg2 import sql

# Database connection details
DB_HOST = "172.16.16.54"
DB_PORT = "5432"
DB_NAME = "qor"
DB_USER = "postgres"
DB_PASSWORD = "root"

# Path to your CSV file
CSV_FILE_Path = r"/home/eswar/esw/vanna/place_qor.csv"
# Connect to PostgreSQL
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

# Read the CSV file into a DataFrame
df = pd.read_csv(CSV_FILE_Path)
df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()  # Clean column names

# Generate table name dynamically
dynamic_path = os.path.basename(CSV_FILE_Path).replace("\\", "_").replace("/", "_").replace(".", "_").replace("-", "_").lower()
table_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in dynamic_path)

# Map pandas dtypes to PostgreSQL column types
def map_dtype(dtype, col_name):
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(dtype):
        if "percent" in col_name.lower() or "%" in col_name.lower():
            return "FLOAT"
        return "DOUBLE PRECISION"
    return "TEXT"

columns = df.columns.tolist()
types = [map_dtype(df[col].dtype, col) for col in columns]

# Check if the table exists
cursor.execute(
    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s);",
    (table_name,)
)
table_exists = cursor.fetchone()[0]

if not table_exists:
    # Create table if it does not exist
    create_table_query = sql.SQL(
        "CREATE TABLE {} ({});"
    ).format(
        sql.Identifier(table_name),
        sql.SQL(', ').join(
            sql.SQL("{} {}").format(sql.Identifier(col), sql.SQL(data_type)) for col, data_type in zip(columns, types)
        )
    )
    cursor.execute(create_table_query)
    conn.commit()
else:
    # Check if columns in the CSV file match the table schema
    cursor.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name = %s;",
        (table_name,)
    )
    existing_columns = [row[0] for row in cursor.fetchall()]
    
    for col, col_type in zip(columns, types):
        if col not in existing_columns:
            # Add missing columns
            alter_table_query = sql.SQL(
                "ALTER TABLE {} ADD COLUMN {} {};"
            ).format(
                sql.Identifier(table_name),
                sql.Identifier(col),
                sql.SQL(col_type)
            )
            cursor.execute(alter_table_query)
            conn.commit()

# Insert data into the table
insert_query = sql.SQL(
    "INSERT INTO {} ({}) VALUES ({}) ON CONFLICT DO NOTHING;"
).format(
    sql.Identifier(table_name),
    sql.SQL(', ').join(sql.Identifier(col) for col in columns),
    sql.SQL(', ').join(sql.Placeholder() for _ in columns)
)

cursor.executemany(insert_query, df.values.tolist())
conn.commit()

# Close the connection
cursor.close()
conn.close()

print(f"Data loaded successfully into PostgreSQL table: {table_name}")
