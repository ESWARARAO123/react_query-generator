# gui.py
import streamlit as st
import pandas as pd
from database import execute_sql, get_schema
from model import generate_sql

st.set_page_config(page_title="Local Vanna + Ollama", layout="wide")
st.title("?? PostgreSQL Natural Language Query (Dynamic Schema)")

# Load schema once
schema = get_schema()

# Input form
with st.form("query_form"):
    user_query = st.text_input("Enter your question:")
    submit = st.form_submit_button("Generate SQL & Run")

if submit and user_query:
    with st.spinner("?? Generating SQL..."):
        sql = generate_sql(user_query, schema)
        st.code(sql, language="sql")
    
    with st.spinner("?? Executing SQL..."):
        try:
            df = execute_sql(sql)
            st.success("? Query executed successfully!")
            st.dataframe(df)
        except Exception as e:
            st.error(f"? Error: {e}")