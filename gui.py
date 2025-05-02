'''# gui.py
import streamlit as st
import pandas as pd
from database import execute_sql, get_schema
from model import generate_sql

# Set page config with icon from static folder
st.set_page_config(
    page_title="PostgreSQL Query Assistant",
    page_icon="static/query-analysis.png"  # Browser tab icon
)

# Title with icon and text
st.image("static/brain.png", width=30, caption="")  # Icon
st.title(" PostgreSQL Natural Language Query Assistant (AI-Powered)")

# Load schema once
schema = get_schema()

# Input form
with st.form("query_form"):
    user_query = st.text_input("Enter your question:")
    submit = st.form_submit_button("Generate SQL & Run")

if submit and user_query:
    # Show spinner icon with label
    st.image("static/generative.png", width=25, caption="")  # Spinner icon
    st.write("Generating SQL...")
    
    with st.spinner():
        sql = generate_sql(user_query, schema)
        st.code(sql, language="sql")
    
    # Show spinner icon for execution
    st.image("static/task-management.png", width=25, caption="")  # Spinner icon
    st.write("Executing SQL...")
    
    with st.spinner():
        try:
            df = execute_sql(sql)
            # Show success icon
            st.image("static/database-management.png", width=25, caption="")  # Success icon
            st.success("Query executed successfully!")
            st.dataframe(df)
        except Exception as e:
            # Show error icon
            st.image("static/browser.png", width=25, caption="")  # Error icon
            st.error(f"Error: {e}")'''
# gui.py
import streamlit as st
import pandas as pd
from database import execute_sql, get_schema
from model import generate_sql

# Set page config with icon (still appears in browser tab)
st.set_page_config(
    page_title="PostgreSQL Query Assistant",
    page_icon="static/query-analysis.png"
)

# Title with icon + text side-by-side
col1, col2 = st.columns([1, 10])
with col1:
    st.image("static/brain.png", width=30)
with col2:
    st.title(" PostgreSQL Natural Language Query Assistant (AI-Powered)")

# Load schema once
schema = get_schema()

# Input form
with st.form("query_form"):
    user_query = st.text_input("Enter your question:")
    submit = st.form_submit_button("Generate SQL & Run")

if submit and user_query:
    # Generating SQL (side-by-side icon + text)
    col1, col2 = st.columns([1, 10])
    with col1:
        st.image("static/generative.png", width=25)
    with col2:
        st.write("Generating SQL...")
    
    with st.spinner():
        sql = generate_sql(user_query, schema)
        st.code(sql, language="sql")
    
    # Executing SQL (side-by-side icon + text)
    col1, col2 = st.columns([1, 10])
    with col1:
        st.image("static/task-management.png", width=25)
    with col2:
        st.write("Executing SQL...")
    
    with st.spinner():
        try:
            df = execute_sql(sql)
            # Success message (side-by-side icon + text)
            col1, col2 = st.columns([1, 10])
            with col1:
                st.image("static/database-management.png", width=25)
            with col2:
                st.success("Query executed successfully!")
            
            st.dataframe(df)
        except Exception as e:
            # Error message (side-by-side icon + text)
            col1, col2 = st.columns([1, 10])
            with col1:
                st.image("static/browser.png", width=25)
            with col2:
                st.error(f"Error: {e}")