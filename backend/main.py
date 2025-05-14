from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import subprocess
import json
import os
import tempfile
import base64
import pandas as pd
from database import execute_sql, get_schema, get_tables
from model import generate_sql
from typing import List, Dict, Any, Optional
from urllib.parse import quote

app = FastAPI(
    title="Chat2SQL API",
    description="API for converting natural language queries to SQL and executing them",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class CSVDownloadRequest(BaseModel):
    data: list
    columns: list
    filename: str

class QueryResponse(BaseModel):
    sql: str
    data: List[Dict[str, Any]]
    columns: List[str]
    curl_command: Optional[str] = None

class DatabaseSchema(BaseModel):
    tables: Dict[str, Dict[str, Any]]

class SchemaResponse(BaseModel):
    database_schema: DatabaseSchema

class TablesResponse(BaseModel):
    table_list: List[str]

def generate_graph_code(data, columns):
    # Create a temporary Python file for graph generation
    graph_code = f"""
import matplotlib.pyplot as plt
import pandas as pd
import json
import base64
from io import BytesIO

# Convert data to DataFrame
data = {json.dumps(data)}
columns = {json.dumps(columns)}
df = pd.DataFrame(data, columns=columns)

# Create figure and axis
plt.figure(figsize=(10, 6))

# Create bar plot
df.plot(kind='bar', x=columns[0], y=columns[1:])

# Customize the plot
plt.title('Data Visualization')
plt.xlabel(columns[0])
plt.ylabel('Values')
plt.xticks(rotation=45)
plt.tight_layout()

# Save plot to a bytes buffer
buf = BytesIO()
plt.savefig(buf, format='png')
buf.seek(0)

# Convert to base64
img_str = base64.b64encode(buf.getvalue()).decode()
print(img_str)  # This will be captured by subprocess
"""
    return graph_code

def clean_sql_query(sql_query):
    """Clean and format SQL query for execution"""
    # Remove markdown formatting
    sql = sql_query.replace('```sql', '').replace('```', '').strip()
    
    # Remove multiple semicolons and ensure only one at the end
    sql = sql.replace(';', ' ').strip()
    if not sql.endswith(';'):
        sql += ';'
    
    # Remove any extra whitespace
    sql = ' '.join(sql.split())
    
    return sql

@app.get("/api/schema", response_model=SchemaResponse, tags=["Database"])
async def get_database_schema():
    """
    Get the complete database schema.
    
    Returns:
        SchemaResponse: The database schema including tables and their columns
    """
    try:
        schema = get_schema()
        return {"database_schema": {"tables": schema}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tables", response_model=TablesResponse, tags=["Database"])
async def get_available_tables():
    """
    Get list of available tables in the database.
    
    Returns:
        TablesResponse: List of table names
    """
    try:
        tables = get_tables()
        return {"table_list": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute", response_model=QueryResponse, tags=["Query"])
async def execute_query_endpoint(request: QueryRequest):
    """
    Execute a natural language query and return the results.
    
    Args:
        request (QueryRequest): The natural language query
        
    Returns:
        QueryResponse: The SQL query, results data, column names, and curl command
    """
    try:
        # Get schema first
        schema = get_schema()
        
        # Check if the query is about drawing a graph
        if "draw a bar graph" in request.query.lower():
            # Let the LLM understand the query and database structure
            modified_query = f"""
            For the following request: "{request.query}"
            First analyze the database schema to understand the tables and columns.
            Then generate a SQL query that will:
            1. Identify the relevant tables and columns from the schema
            2. Create appropriate joins between tables
            3. Select the necessary columns for visualization
            4. Apply any required filters based on the user's request
            5. Group the data appropriately for the visualization
            """
            
            sql_query = generate_sql(modified_query, schema)
            sql_query = clean_sql_query(sql_query)
            
            try:
                df = execute_sql(sql_query)
            except Exception as e:
                # If there's an error, let the LLM fix it
                error_message = str(e)
                fix_query = f"""
                The previous SQL query failed with error: {error_message}
                Please analyze the error and generate a corrected SQL query that:
                1. Resolves any ambiguous column references
                2. Maintains the original query intent
                3. Uses proper table aliases and column qualifications
                """
                sql_query = generate_sql(fix_query, schema)
                sql_query = clean_sql_query(sql_query)
                df = execute_sql(sql_query)
            
            if df.empty:
                raise HTTPException(status_code=400, detail="No data available for visualization")
            
            # Convert DataFrame to dict for JSON response
            result = {
                'data': df.to_dict(orient='records'),
                'columns': df.columns.tolist()
            }
            
            # Generate and execute graph code
            graph_code = generate_graph_code(result['data'], result['columns'])
            
            # Create a temporary file for the graph code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(graph_code)
                temp_file = f.name
            
            try:
                # Run the graph generation code
                process = subprocess.run(['python', temp_file], 
                                      capture_output=True, 
                                      text=True, 
                                      check=True)
                
                # Get the base64 image string from output
                img_str = process.stdout.strip()
                
                # Clean up the temporary file
                os.unlink(temp_file)
                
                # Generate curl command
                curl_command = f"""curl -X POST http://localhost:5000/api/execute \\
-H "Content-Type: application/json" \\
-d '{{"query": "{quote(request.query)}"}}'"""

                return {
                    "sql": sql_query,
                    "data": result['data'],
                    "columns": result['columns'],
                    "graph": img_str,
                    "curl_command": curl_command
                }
            except subprocess.CalledProcessError as e:
                raise HTTPException(status_code=500, detail=f"Graph generation failed: {str(e)}")
            finally:
                # Ensure temporary file is cleaned up
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
        
        # Regular query execution
        sql_query = generate_sql(request.query, schema)
        sql_query = clean_sql_query(sql_query)
        
        try:
            df = execute_sql(sql_query)
        except Exception as e:
            # If there's an error, let the LLM fix it
            error_message = str(e)
            fix_query = f"""
            The previous SQL query failed with error: {error_message}
            Please analyze the error and generate a corrected SQL query that:
            1. Resolves any ambiguous column references
            2. Maintains the original query intent
            3. Uses proper table aliases and column qualifications
            """
            sql_query = generate_sql(fix_query, schema)
            sql_query = clean_sql_query(sql_query)
            df = execute_sql(sql_query)
        
        # Generate curl command
        curl_command = f"""curl -X POST http://localhost:5000/api/execute \\
-H "Content-Type: application/json" \\
-d '{{"query": "{quote(request.query)}"}}'"""

        return {
            "sql": sql_query,
            "data": df.to_dict(orient='records'),
            "columns": df.columns.tolist(),
            "curl_command": curl_command
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/download-csv")
async def download_csv(request: CSVDownloadRequest):
    try:
        # Create DataFrame from the data
        df = pd.DataFrame(request.data, columns=request.columns)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            # Save DataFrame to CSV
            df.to_csv(tmp.name, index=False)
            
            # Read the file content
            with open(tmp.name, 'rb') as f:
                content = f.read()
            
            # Clean up
            os.unlink(tmp.name)
            
            # Return the CSV content with proper headers
            return JSONResponse(
                content={
                    "filename": request.filename,
                    "content": base64.b64encode(content).decode('utf-8')
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)