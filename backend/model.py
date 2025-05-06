# model.py
import ollama
from config import OLLAMA_MODEL

def generate_sql(natural_language_query, schema):
    """Generate SQL using Ollama LLM with schema context"""
    prompt = f"""
You are a PostgreSQL expert. Convert the following natural language query into SQL.
Use the provided schema to understand table/column relationships.

Schema:
{schema}

Query:
{natural_language_query}

Return ONLY the SQL query, no explanations.
"""
    response = ollama.generate(model=OLLAMA_MODEL, prompt=prompt)
    return response['response'].strip()