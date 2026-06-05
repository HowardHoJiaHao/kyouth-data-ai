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
        with st.status("Analyzing your request...", expanded=True) as status:
            # 1. Generate SQL
            st.write("Generating SQL query...")
            schema = """
            Table: spending 
            Columns: id (INTEGER), date (TEXT, YYYY-MM-DD), description (TEXT), price (REAL), category (TEXT)

            ALLOWED CATEGORIES:
            Food, Transport, Utilities & Bill, Study & Academic, Household & Cleaning, Selfcare & Health, Laundry, Entertainment & Treat, Others

            RULES:
            1. ONLY use the 'spending' table.
            2. DO NOT use JOINs.
            3. Use simple SELECT and GROUP BY queries.
            4. For date filtering, use the 'date' column directly.
            5. Return ONLY the raw SQL code. No markdown formatting, no explanations.
            """
            prompt = f"""
            You are a SQL expert. 
            Database Schema and Rules: {schema}
            User Question: '{user_query}'

            Convert the user question into a valid SQLite query.
            """
            response = ollama.chat(model='gemma2:2b', messages=[{'role': 'user', 'content': prompt}])
            sql = response['message']['content'].split("</think>")[-1].replace("```sql", "").replace("```", "").strip()
            
            # 2. Execute SQL
            st.write("Querying database...")
            result = execute_natural_language_query(sql)
            
            # 3. Explain the result (The new step!)
            st.write("Generating explanation...")
            if isinstance(result, str) and "Error" in result:
                explanation = "I couldn't process that query correctly."
            else:
                explain_prompt = f"""
                User asked: '{user_query}'
                Database returned this data: 
                {result.to_string() if result is not None else 'No data'}
                
                Explain this result to the user in a friendly, conversational tone. 
                Keep it concise.
                """
                explain_res = ollama.chat(model='gemma2:2b', messages=[{'role': 'user', 'content': explain_prompt}])
                explanation = explain_res['message']['content'].split("</think>")[-1].strip()
            
            status.update(label="Analysis complete!", state="complete", expanded=False)

        # Final UI Display
        st.write("### AI Insight:")
        st.info(explanation)
        
        with st.expander("🔍 See technical details"):
            # st.write("**SQL Query:**")
            # st.code(sql, language="sql")
            st.write("**Raw Data:**")
            st.write(result)

with tab3:
    st.header("Spending Analytics")
    df = get_all_expenses()
    
    if df is not None and not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        # Create a 'month' column for easier grouping (e.g., '2026-06')
        df['month'] = df['date'].dt.to_period('M').astype(str)
        
        # 1. Stacked Bar Chart: Monthly spending broken down by category
        st.subheader("Monthly Spending by Category (Stacked)")
        monthly_cat_df = df.groupby(['month', 'category'])['price'].sum().reset_index()
        fig_stacked = px.bar(
            monthly_cat_df, 
            x='month', 
            y='price', 
            color='category',
            title="Total Spending per Month by Category",
            labels={'price': 'Amount (RM)', 'month': 'Month'}
        )
        st.plotly_chart(fig_stacked, width='stretch')

        col1, col2 = st.columns(2)
        
        with col1:
            # 2. Pie Chart: Total distribution across all time
            st.subheader("Overall Spending Distribution")
            total_cat_df = df.groupby('category')['price'].sum().reset_index()
            fig_pie = px.pie(
                total_cat_df, 
                values='price', 
                names='category',
                hole=0.3
            )
            st.plotly_chart(fig_pie, width='stretch')
            
        with col2:
            # 3. Trend Line: Average daily spending
            st.subheader("Daily Average Trend")
            daily_df = df.resample('D', on='date')['price'].sum().reset_index()
            fig_line = px.line(daily_df, x='date', y='price', title="Daily Spending Activity")
            st.plotly_chart(fig_line, width='stretch')
            
    else:
        st.info("Log some expenses to see your charts!")