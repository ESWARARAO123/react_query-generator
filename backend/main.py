from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import execute_sql, get_schema
from model import generate_sql

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.get("/api/schema")
async def get_database_schema():
    try:
        schema = get_schema()
        return {"schema": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute")
async def execute_query(request: QueryRequest):
    try:
        # Generate SQL from natural language
        sql = generate_sql(request.query, get_schema())
        
        # Execute the SQL query
        result = execute_sql(sql)
        
        # Convert DataFrame to dict for JSON response
        return {
            "sql": sql,
            "data": result.to_dict(orient='records'),
            "columns": result.columns.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)