import streamlit as st
import ollama
import pandas as pd
import plotly.express as px
from database import add_expense_to_db, get_all_expenses, execute_natural_language_query

st.set_page_config(page_title="Money Manager", layout="wide")
st.title("💰 Howard's Money Manager")

tab1, tab2, tab3 = st.tabs(["➕ Add Expense", "🤖 Chatbot", "📊 Dashboard"])

with tab1:
    st.header("Log New Expense")
    with st.form("expense_form"):
        desc = st.text_input("Description")
        price = st.number_input("Price (RM)", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Save Expense")
        if submitted and desc:
            add_expense_to_db(desc, price)
            st.success(f"Added '{desc}' successfully!")

with tab2:
    st.header("Financial Assistant")
    user_query = st.text_input("Ask about your spending:")
    if st.button("Ask") and user_query:
        with st.spinner("Analyzing..."):
            # Prompt for SQL generation
            schema = "Table: spending (id, date, description, price, category)"
            prompt = f"You are a SQL expert. Schema: {schema}. Convert '{user_query}' into a SQLite query. Return ONLY the raw SQL code."
            
            response = ollama.chat(model='deepseek-r1:1.5b', messages=[{'role': 'user', 'content': prompt}])
            content = response['message']['content']
            
            # Clean up thinking tags and markdown
            sql = content.split("</think>")[-1].replace("```sql", "").replace("```", "").strip()
            
            # Execute and display
            result = execute_natural_language_query(sql)
            st.write(result)

with tab3:
    st.header("Spending Analytics")
    df = get_all_expenses()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Monthly Trend")
            monthly = df.resample('ME', on='date')['price'].sum().reset_index()
            st.plotly_chart(px.line(monthly, x='date', y='price', markers=True), use_container_width=True)
        with col2:
            st.subheader("Expenses by Category")
            cat_df = df.groupby('category')['price'].sum().reset_index()
            st.plotly_chart(px.bar(cat_df, x='category', y='price', color='category'), use_container_width=True)
    else:
        st.info("Log some expenses to see your charts!")