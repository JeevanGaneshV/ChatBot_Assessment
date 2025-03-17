# 🏠 Real Estate SQL Chatbot

A **Streamlit-powered chatbot** that allows users to interact with a **PostgreSQL real estate database** using natural language. This chatbot converts user queries into **SQL commands**, executes them, and provides easy-to-understand explanations of the results.

## 🚀 Features
- **💾 Database Connectivity:** Connects to a PostgreSQL database or uses a mock database for testing.
- **🧠 AI-Powered SQL Generation:** Uses the **Ollama LLM** (`llama3.2` model) to convert natural language questions into SQL queries.
- **📊 Query Execution & Explanation:** Runs SQL queries, retrieves results, and provides AI-generated insights in real estate terms.
- **🖥️ Interactive UI:** Built with **Streamlit** for a seamless chatbot-like experience.
- **⚡ Easy Setup:** Automatically installs required dependencies and provides a simple configuration interface.

## 🏗️ Installation
Ensure you have Python installed, then uncomment the dependencies code lines and let the script handle dependency installation automatically.

## 🛠️ How to Use
1. **Run the chatbot:**
   ```sh
   streamlit run app.py
   ```
2. **Configure database settings** via the sidebar.
3. **Ask questions** about your real estate data.
4. **View SQL queries, results, and explanations** in the UI.

## ⚙️ Configuration
- **PostgreSQL Credentials:** Set database host, port, username, and password in the sidebar.
- **Mock Mode:** Use sample real estate data for testing without a database.
- **LLM Timeout:** Adjust the processing time for AI-generated responses.

## 🛡️ Dependencies
- `streamlit`
- `ollama`
- `langchain-core`
- `langchain-community`
- `psycopg2-binary`
- `sqlalchemy`
- `pandas`

## 📌 Notes
- Ensure **Ollama is running** and the `llama3.2` model is available.
- If using a database, make sure **PostgreSQL is accessible**.

## 📜 License
This project is licensed under the **Apache License 2.0**.

---


