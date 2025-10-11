"""
Main Streamlit Application Entry Point
AI Assistant with RAG & Reasoning Agent
"""
import streamlit as st
from dotenv import load_dotenv
import os
import uuid

from config.settings import PAGE_CONFIG, FIRESTORE_CONFIG
from agents.agent_setup import setup_agent
from ui.sidebar import render_sidebar
from ui.chat import render_chat_interface
from utils.helpers import generate_session_title

# Load environment variables
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Page configuration
st.set_page_config(**PAGE_CONFIG)


def _auto_load_last_session():
    """Auto-load the most recent session on app start"""
    # Only run once per session
    if st.session_state.get("session_loaded", False):
        return
    try:
        from utils.firestore_manager import init_firestore

        # Quick check: if cloud storage disabled, skip
        if not FIRESTORE_CONFIG.get("enabled", False):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.session_loaded = True
            return
        
        # Initialize Firestore manager
        firestore_manager = init_firestore(FIRESTORE_CONFIG["project_id"])

        # If not connected, don't wait - create new session
        if not firestore_manager.is_connected():
            # No cloud connection, create new session
            st.session_state.session_id = str(uuid.uuid4())
            return
        
        # Get all sessions
        sessions = firestore_manager.list_sessions()
        
        if sessions:
            # Load the most recent session (last in list)
            last_session = sessions[-1]
            st.session_state.session_id = last_session
            
            # Load messages from that session
            messages = firestore_manager.load_messages(last_session)
            if messages:
                st.session_state.messages = messages
                
                # Generate session name from first message
                first_user_msg = next((m for m in messages if m["role"] == "user"), None)
                if first_user_msg:
                    st.session_state.session_name = generate_session_title(first_user_msg["content"])
        else:
            # No sessions, create new one
            st.session_state.session_id = str(uuid.uuid4())

        st.session_state.session_loaded = True
            
    except Exception as e:
        # If anything fails, just create a new session
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.session_loaded = True


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
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "session_name" not in st.session_state:
        st.session_state.session_name = None
    if "session_loaded" not in st.session_state:
        st.session_state.session_loaded = False
    
    # Auto-load last session (only once, and only if enabled in config)
    if (FIRESTORE_CONFIG.get("enabled", False) and 
        FIRESTORE_CONFIG.get("auto_load", False) and 
        not st.session_state.session_loaded):
        _auto_load_last_session()


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