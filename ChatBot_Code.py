import sys
import subprocess
import os

# # Install necessary dependencies
# def install_packages():
#     required_packages = [
#         "streamlit",
#         "ollama",
#         "langchain-core",
#         "langchain-community",
#         "psycopg2-binary",  # Changed back to psycopg2 for PostgreSQL
#         "sqlalchemy",
#         "pandas"
#     ]
    
#     python_exe = sys.executable
#     subprocess.check_call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
#     subprocess.check_call([python_exe, "-m", "pip", "install"] + required_packages)
#     print("All packages installed successfully!")

# # Check and install packages if running for the first time
# install_packages()



# Importing the necessary packages
import streamlit as st
import ollama
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
import pandas as pd
import time
import concurrent.futures

# Streamlit page config
st.set_page_config(page_title="Real Estate SQL Chatbot", page_icon="🏠", layout="wide")

# Database connection settings
if 'db_connected' not in st.session_state:
    st.session_state.db_connected = False
if 'db_config' not in st.session_state:
    st.session_state.db_config = {
        "DB_USER": "postgres",  # Default PostgreSQL user
        "DB_PASSWORD": "admin",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",  # Default PostgreSQL port
        "DB_NAME": "postgres"  # Your database name
    }

def connect_to_database():
    try:
        # PostgreSQL connection string format
        db_uri = f"postgresql://{st.session_state.db_config['DB_USER']}:{st.session_state.db_config['DB_PASSWORD']}@{st.session_state.db_config['DB_HOST']}:{st.session_state.db_config['DB_PORT']}/{st.session_state.db_config['DB_NAME']}"
        db = SQLDatabase.from_uri(db_uri)
        st.session_state.db = db
        st.session_state.db_schema = db.get_table_info()
        st.session_state.db_connected = True
        return True
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return False

def use_mock_database():
    MOCK_SCHEMA = """
    CREATE TABLE public.realestatedata (
        id SERIAL PRIMARY KEY,
        address VARCHAR(200),
        city VARCHAR(100),
        state VARCHAR(50),
        zip_code VARCHAR(20),
        price NUMERIC(15,2),
        bedrooms INTEGER,
        bathrooms NUMERIC(4,1),
        square_feet INTEGER,
        year_built INTEGER,
        property_type VARCHAR(50),
        listing_date DATE,
        status VARCHAR(20)
    );
    """
    st.session_state.db_schema = MOCK_SCHEMA
    st.session_state.using_mock_db = True
    st.session_state.db_connected = True
    
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to communicate with Ollama LLM with timeout
def query_ollama(prompt: str, timeout=960) -> str:
    try:
        # Use concurrent.futures to implement timeout
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                ollama.chat,
                model="llama3.2",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Wait for the result with timeout
            try:
                response = future.result(timeout=timeout)
                return response["message"]["content"].strip()
            except concurrent.futures.TimeoutError:
                # Handle timeout
                return "I'm sorry, the request timed out. Please try again with a simpler question."
    except Exception as e:
        return f"Error communicating with LLM: {str(e)}"

class SQLChatbot:
    def __init__(self):
        self.chat_history = []
    
    def generate_sql(self, user_query: str) -> str:
        schema_info = f"""
        Database Schema: {st.session_state.db_schema}
        
        Important Notes:
        - The table name is 'realestatedata' in the 'public' schema
        - All queries should use 'public.realestatedata' as the table reference
        """
        
        system_prompt = f"""
        You are an expert SQL assistant specialized in PostgreSQL. Convert the user's natural language question into a SQL query.
        {schema_info}
        Return ONLY the SQL query, nothing else. Make sure to properly qualify table names with schema.
        """
        
        with st.spinner("Generating SQL query..."):
            result = query_ollama(system_prompt + "\nUser: " + user_query)
        
        return result
    
    def explain_results(self, user_query: str, sql_query: str, result) -> str:
        # Convert result to string if it's a dataframe
        if isinstance(result, pd.DataFrame):
            if result.empty:
                result_str = "No results found for this query."
            else:
                # Limit to showing only 10 rows in explanation to avoid token limit issues
                display_df = result.head(10)
                result_str = display_df.to_markdown()
                if len(result) > 10:
                    result_str += f"\n\n(Showing 10 of {len(result)} total results)"
        else:
            result_str = str(result)
        
        system_prompt = f"""
        You are an expert real estate data analyst. Explain the SQL results in simple terms.\n
        User Question: {user_query}\n
        SQL Query: {sql_query}\n
        Query Results: {result_str}\n
        Give a clear and insightful summary. Highlight key patterns or insights from the data.
        Focus on explaining what the data means in real estate terms.
        """
        
        with st.spinner("Analyzing results..."):
            result = query_ollama(system_prompt)
        
        return result
    
    def process_query(self, user_query: str):
        # Generate SQL query
        sql_query = self.generate_sql(user_query)
        
        # Check if the LLM failed to generate a query
        if sql_query.startswith("Error") or sql_query.startswith("I'm sorry"):
            return sql_query, None, "Could not generate a valid SQL query. Please try again."
        
        # Execute the query
        with st.spinner("Executing SQL query..."):
            if hasattr(st.session_state, 'using_mock_db') and st.session_state.using_mock_db:
                # For mock database, we'll create a sample real estate dataframe
                time.sleep(1)  # Simulate query execution time
                result = pd.DataFrame({
                    'id': [1, 2, 3, 4, 5],
                    'address': ['123 Main St', '456 Oak Ave', '789 Pine Rd', '101 Maple Dr', '202 Cedar Ln'],
                    'city': ['Austin', 'Austin', 'Dallas', 'Houston', 'San Antonio'],
                    'state': ['TX', 'TX', 'TX', 'TX', 'TX'],
                    'zip_code': ['78701', '78704', '75201', '77002', '78205'],
                    'price': [450000, 525000, 375000, 620000, 289000],
                    'bedrooms': [3, 4, 2, 5, 3],
                    'bathrooms': [2.5, 3.0, 2.0, 4.5, 2.0],
                    'square_feet': [2100, 2800, 1500, 3500, 1800],
                    'year_built': [2005, 2015, 1998, 2020, 2008],
                    'property_type': ['Single Family', 'Single Family', 'Condo', 'Single Family', 'Townhouse'],
                    'listing_date': ['2024-03-01', '2024-02-15', '2024-03-10', '2024-01-20', '2024-02-28'],
                    'status': ['Active', 'Active', 'Pending', 'Sold', 'Active']
                })
            else:
                try:
                    # Execute the SQL query against PostgreSQL and convert results to DataFrame
                    engine = st.session_state.db._engine
                    with engine.connect() as conn:
                        result = pd.read_sql(sql_query, conn)
                except Exception as e:
                    result = f"Error executing query: {str(e)}"
        
        # Generate explanation
        if isinstance(result, str) and result.startswith("Error"):
            explanation = f"There was an error executing your query: {result}"
        else:
            explanation = self.explain_results(user_query, sql_query, result)
        
        return sql_query, result, explanation

st.title("Real Estate Database Query Assistant 🏠")

with st.sidebar:
    st.header("Database Configuration")
    with st.form("db_connection_form"):
        st.session_state.db_config["DB_USER"] = st.text_input("Username", st.session_state.db_config["DB_USER"])
        st.session_state.db_config["DB_PASSWORD"] = st.text_input("Password", st.session_state.db_config["DB_PASSWORD"], type="password")
        st.session_state.db_config["DB_HOST"] = st.text_input("Host", st.session_state.db_config["DB_HOST"])
        st.session_state.db_config["DB_PORT"] = st.text_input("Port", st.session_state.db_config["DB_PORT"])
        st.session_state.db_config["DB_NAME"] = st.text_input("Database Name", st.session_state.db_config["DB_NAME"])
        connect_button = st.form_submit_button("Connect to Database")
    
    if connect_button:
        with st.spinner("Connecting to database..."):
            if connect_to_database():
                st.success("Connected to the database!")
                st.write("Schema loaded with tables:")
                st.code(st.session_state.db_schema)
    
    if st.button("Use Mock Database"):
        use_mock_database()
        st.success("Using mock database mode with sample real estate data.")
    
    # LLM Configuration
    st.header("LLM Configuration")
    if 'llm_timeout' not in st.session_state:
        st.session_state.llm_timeout = 30
    st.session_state.llm_timeout = st.slider("LLM Timeout (seconds)", 60, 480, st.session_state.llm_timeout)
    
    # Check Ollama Status
    if st.button("Check Ollama Status"):
        try:
            with st.spinner("Checking Ollama..."):
                models = ollama.list()
                if 'models' in models and models['models']:
                    model_names = [m.get('name', 'Unknown') for m in models['models']]
                    st.success(f"Ollama is running! Available models: {', '.join(model_names)}")
                else:
                    st.warning("Ollama is running but no models were found. Please pull the llama3.2 model.")
        except Exception as e:
            st.error(f"Ollama error: {str(e)}")
            st.info("Make sure Ollama is running and llama3.2 model is pulled.")

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = SQLChatbot()

# Main chat interface
st.subheader("Ask questions about your real estate database")

# Display chat history
for message in st.session_state.get("chat_history", []):
    with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
        st.write(message.content)

if st.session_state.db_connected:
    user_query = st.chat_input("Ask a question about the real estate data...")
    if user_query:
        # Add user message to chat
        with st.chat_message("user"):
            st.write(user_query)
        
        # Add to history
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        
        # Process query with progress indicators
        with st.spinner("Processing your query..."):
            sql_query, result, explanation = st.session_state.chatbot.process_query(user_query)
        
        # Display assistant response
        with st.chat_message("assistant"):
            if sql_query.startswith("Error") or sql_query.startswith("I'm sorry"):
                st.error(sql_query)
            else:
                st.subheader("SQL Query")
                st.code(sql_query, language="sql")
                
                st.subheader("Results")
                if isinstance(result, pd.DataFrame):
                    if result.empty:
                        st.info("No results found for this query.")
                    else:
                        st.dataframe(result, use_container_width=True)
                        st.caption(f"Found {len(result)} records.")
                elif result is not None:
                    st.write(result)
                
                st.subheader("Explanation")
                st.write(explanation)
        
        # Add assistant response to history
        st.session_state.chat_history.append(AIMessage(content=explanation))
else:
    st.info("Please connect to a database or use mock mode to start.")
