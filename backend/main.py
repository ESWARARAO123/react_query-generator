from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import os
import tempfile
import base64
from database import execute_sql, get_schema
from model import generate_sql

app = FastAPI()

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

@app.get("/api/schema")
async def get_database_schema():
    try:
        schema = get_schema()
        return {"schema": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute")
async def execute_query_endpoint(request: QueryRequest):
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
                
                return {
                    "sql": sql_query,
                    "data": result['data'],
                    "columns": result['columns'],
                    "graph": img_str
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
            
        return {
            "sql": sql_query,
            "data": df.to_dict(orient='records'),
            "columns": df.columns.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)