# model.py
import ollama
from config import OLLAMA_MODEL

def generate_sql(natural_language_query, schema):
    """Generate SQL using Ollama LLM with schema context"""
    prompt = f"""
You are a PostgreSQL expert. Convert the following natural language query into SQL.
Use the provided schema to understand table/column relationships.

Important rules:
1. Return ONLY the specific columns and rows that are directly asked for in the query
2. Do not include any additional columns or data unless explicitly requested
3. For queries asking about specific values, return the exact values without using AVG or other aggregations
4. Only use aggregations (AVG, SUM, COUNT, etc.) when explicitly requested
5. When querying for a specific value, use WHERE clauses to filter the exact data
6. Return all matching rows unless specifically asked to limit the results
7. If the query asks for a single value, use LIMIT 1
8. Do not include any extra columns in the SELECT statement unless they are specifically requested
9. For text searches, use ILIKE or LOWER()/UPPER() to make the search case-insensitive
10. When searching for text, convert both the search term and the column to the same case (either both LOWER or both UPPER)
11. For partial text matches, use ILIKE with % wildcards
12. When referencing column names with spaces, use double quotes like "Column Name"
13. For column names in the schema, match them case-insensitively (e.g., "buffer count" should match "Buffer count")
14. When the query mentions a column name, check the schema for the exact column name and use that in the SQL
15. If a column name in the query doesn't match exactly, try to find the closest match in the schema
16. Understand the intent of the query - if asking for a value of a metric, return both the metric name and its value
17. When asking for a specific metric's value, include both the metric name and its value in the SELECT statement
18. For queries about metrics, always include the metric name in the results unless specifically asked not to
19. When the query is about a specific metric, make sure to return both the metric name and its corresponding value
20. If the query is about finding a value for a specific metric, use a WHERE clause to filter for that metric

Schema:
{schema}

Query:
{natural_language_query}

Return ONLY the SQL query, no explanations.
"""
    response = ollama.generate(model=OLLAMA_MODEL, prompt=prompt)
    return response['response'].strip()