"""
Main Streamlit Application Entry Point
AI Assistant with RAG & Reasoning Agent
"""
import os
import streamlit as st
from dotenv import load_dotenv
from config.settings import PAGE_CONFIG
from agents.agent_setup import setup_agent
from ui.sidebar import render_sidebar
from ui.chat import render_chat_interface

# Load environment variables
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Page configuration
st.set_page_config(**PAGE_CONFIG)


def initialize_session_state():
    """Initialize all session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "rag_chain" not in st.session_state:
        st.session_state.rag_chain = None
    if "uploaded_files_names" not in st.session_state:
        st.session_state.uploaded_files_names = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None
    if "rag_chat_history" not in st.session_state:
        st.session_state.rag_chat_history = []


def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Setup agent
    agent_executor = setup_agent()
    
    # Render header
    st.title("🤖 AI Assistant with RAG & Reasoning Agent")
    st.markdown("Ask me anything! I can search the web, check weather, convert currency, look up stocks, calculate, **and answer questions from your documents!**")
    
    # Render sidebar
    render_sidebar()
    
    # Render chat interface
    render_chat_interface(agent_executor)


if __name__ == "__main__":
    main()