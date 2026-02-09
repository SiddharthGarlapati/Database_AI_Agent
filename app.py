import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
import base64

load_dotenv()

st.set_page_config(
    page_title="LangChain Database Agent: Chat with SQL DB",
    layout="wide",
    page_icon="🗄️",
    initial_sidebar_state="expanded",
)

ICON_DIR = Path(__file__).parent / "icons" / "icon.png"
icon_b64 = base64.b64encode(ICON_DIR.read_bytes()).decode("utf-8")

st.markdown(
    f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 1.5rem 1.75rem;
        border-radius: 22px;
        background: rgba(255,255,255,0.06);
        margin-bottom: 1.5rem;
    ">
        <img 
            src="data:image/png;base64,{icon_b64}"
            style="
                width: 160px;
                max-width: none;
                height: auto;
                display: block;
            "
        />
        <div>
            <div style="
                font-size: 2.4rem;
                font-weight: 800;
                line-height: 1.1;
            ">
                LangChain Database Agent
            </div>
            <div style="
                margin-top: 0.5rem;
                font-size: 1.2rem;
                opacity: 0.75;
            ">
                Chat with SQLite or connect to MySQL — the agent writes SQL and answers in plain English.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

st.markdown(
    """
    <style>
      footer {visibility: hidden;}

      /* Keep layout spacing */
      .block-container { padding-top: 3.2rem !important; padding-bottom: 2rem; }

      header[data-testid="stHeader"] {
        background: transparent;
        box-shadow: none;
      }

      div[data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
      }

      /* Sidebar spacing */
      section[data-testid="stSidebar"] { padding-top: 1rem; }
    </style>
    """,
    unsafe_allow_html=True
)





LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = ["Use SQlite3 - Student.db", "Connect to SQL Database"]

with st.sidebar:
    st.markdown("## ⚙️ Controls")
    st.caption("Choose a database, provide credentials, and start querying.")

    st.divider()

    st.markdown("### 🗃️ Database")
    selected_opt = st.radio(
        label="Choose a DB to chat",
        options=radio_opt,
        label_visibility="collapsed"
    )

    if radio_opt.index(selected_opt) == 1:
        db_uri = MYSQL
        st.markdown("**MySQL connection**")
        mysql_host = st.text_input("Provide the mysql host")
        mysql_user = st.text_input("MySQL user")
        mysql_password = st.text_input("MySQL password", type = "password")
        mysql_db = st.text_input("MySQL Database")

    else:
        db_uri = LOCALDB  


    st.divider()

    st.markdown("### 🔑 Groq API Key")

    api_key = st.text_input(
        "Groq API key",
        type="password",
        label_visibility="collapsed"
    )


    if not db_uri:
        st.info("Please enter the database information")

    if not api_key:
        st.info("Please enter the groq api key")
        st.stop()


llm = ChatGroq(groq_api_key= api_key , model = "llama-3.3-70b-versatile",streaming = True)

@st.cache_resource(ttl = "2h")
def configure_db(db_uri,mysql_host = None, mysql_user = None, mysql_password = None, mysql_db = None):
    if db_uri == LOCALDB:
        db_filepath = (Path(__file__).parent/"student.db").absolute()
        print(db_filepath)
        creator = lambda : sqlite3.connect(f"file:{db_filepath}?mode=ro", uri = True)
        return SQLDatabase(create_engine("sqlite:///", creator = creator))
    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("please provide all the mysql connection details")
            st.stop()
        else:
            return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))    

if db_uri == MYSQL:
    db = configure_db(db_uri,mysql_host, mysql_user, mysql_password, mysql_db)
else:
    db = configure_db(db_uri)

toolkit = SQLDatabaseToolkit(db = db, llm = llm )


agent = create_sql_agent(
    llm = llm ,
    toolkit= toolkit,
    verbose= True,
    agent_type= AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors = True
)

left, right = st.columns([3, 1])

with right:
    st.markdown("### Session")
    st.write("")

    if db_uri == LOCALDB:
        st.success("DB: SQLite (local)")
        st.caption("File: student.db")
    else:
        st.success("DB: MySQL")
        st.caption(f"Host: {mysql_host}")
        st.caption(f"DB: {mysql_db}")

    st.write("")
    st.markdown("### Model")
    st.caption("Groq")
    st.code("llama-3.3-70b-versatile", language="text")

    st.write("")
    clear_clicked = st.button("🧹 Clear chat", use_container_width=True)

with left: 
    st.markdown("### 💬 Chat")


    if "messages" not in st.session_state or clear_clicked:
        st.session_state["messages" ] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

    user_query = st.chat_input(placeholder= "Ask anything from the database")

    if user_query:
        st.session_state["messages"].append({"role": "user", "content": user_query})
        st.chat_message("user").write(user_query)

        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(st.container())
            with st.spinner("Thinking..."):
                response = agent.run(user_query, callbacks= [st_cb])
            st.session_state["messages"].append({"role": "assistant", "content": response})
            st.write(response)



