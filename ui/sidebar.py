"""
Sidebar UI components
"""
import streamlit as st
from config.settings import TOOL_DESCRIPTIONS, EXAMPLE_QUESTIONS, SUPPORTED_FILE_TYPES, FIRESTORE_CONFIG
from rag.rag_chain import process_documents
from utils.firestore_manager import init_firestore, save_current_chat, load_chat_from_cloud
import uuid

def render_sidebar():
    """Render the complete sidebar with all components"""
    
    # Title and description
    st.sidebar.title("🛠️ Agent Tools")
    st.sidebar.markdown(TOOL_DESCRIPTIONS)
    st.sidebar.markdown("---")

    # Cloud storage section (if enabled)
    if FIRESTORE_CONFIG["enabled"]:
        _render_cloud_storage()
        st.sidebar.markdown("---")
    
    # Document upload section
    _render_document_upload()
    
    st.sidebar.markdown("---")
    
    # Clear chat button
    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.rag_chat_history = []  
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Example questions
    _render_example_questions()


def _render_cloud_storage():
    """Render cloud storage controls"""
    st.sidebar.subheader("☁️ Cloud Storage")

    # Initialize Firestore if not already done
    if "firestore_manager" not in st.session_state:
        firestore_manager = init_firestore(FIRESTORE_CONFIG["project_id"])
        st.session_state.firestore_manager = firestore_manager

    firestore_manager = st.session_state.firestore_manager

    # Show connection status
    if firestore_manager.is_connected():
        st.sidebar.success("✅ Connected to Firestore")
    else:
        st.sidebar.error("❌ Not connected to Firestore")
        st.sidebar.info("💡 Set GOOGLE_APPLICATION_CREDENTIALS in .env")
        return  # Skip further UI if not connected

    # Session ID management
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    st.sidebar.text(f"Session: {st.session_state.session_id[:8]}...")

    # Cloud controls
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("💾 Save to Cloud", use_container_width=True):
            save_current_chat(st.session_state.session_id)

    with col2:
        if st.button("📥 Load from Cloud", use_container_width=True):
            load_chat_from_cloud(st.session_state.session_id)
            st.rerun()

    # Auto-save toggle
    auto_save = st.sidebar.checkbox(
        "Auto-save messages", 
        value=FIRESTORE_CONFIG["auto_save"],
        help="Automatically save each message to cloud"
    )
    st.session_state.auto_save_enabled = auto_save

    # Session management
    with st.sidebar.expander("📋 Session Management"):
        # List saved sessions
        sessions = firestore_manager.list_sessions()

        if sessions:
            st.write(f"**{len(sessions)} saved session(s)**")

            selected_session = st.selectbox(
                "Load a session:",
                options=["Current"] + sessions,
                format_func=lambda x: f"{x[:8]}..." if x != "Current" else x
            )

            if selected_session != "Current":
                if st.button("Load Selected Session"):
                    st.session_state.session_id = selected_session
                    load_chat_from_cloud(selected_session)
                    st.rerun()
        else:
            st.write("No saved sessions")

        # New session button
        if st.button("🆕 New Session"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.rag_chat_history = []
            st.success("New session created!")
            st.rerun()



def _render_document_upload():
    """Render the document upload section"""
    st.sidebar.subheader("📁 Upload Documents")

    # Show status if documents are loaded
    if st.session_state.get('rag_chain') is not None:
        st.sidebar.success("✅ Documents loaded! Ask me about them.")
    else:
        st.sidebar.info("📤 Upload files to ask questions about them")

    st.sidebar.markdown("Upload PDF, Word, or text files to ask questions about them!")
    
    uploaded_files = st.sidebar.file_uploader(
        "Choose files",
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        key="file_uploader"
    )
    
    if uploaded_files:
        current_files = [f.name for f in uploaded_files]
        
        # Check if files have changed
        if current_files != st.session_state.uploaded_files_names:
            with st.sidebar:
                with st.spinner("Processing documents..."):
                    rag_chain = process_documents(uploaded_files)
                    if rag_chain:
                        st.session_state.rag_chain = rag_chain
                        st.session_state.uploaded_files_names = current_files
                        st.session_state.rag_chat_history = []
                        st.success(f"✅ Processed {len(uploaded_files)} document(s)!")
                        st.info("💡 Try asking: 'What's in my document?' or 'Summarize this'")
                    else:
                        st.error("Failed to process documents")
        
        # Show uploaded files
        st.sidebar.markdown("**Uploaded Files:**")
        for file in uploaded_files:
            st.sidebar.text(f"📄 {file.name}")
    else:
        st.session_state.rag_chain = None
        st.session_state.uploaded_files_names = []
        st.session_state.rag_chat_history = []


def _render_example_questions():
    """Render example questions as buttons"""
    st.sidebar.markdown("**💡 Try asking:**")
    
    for example in EXAMPLE_QUESTIONS:
        if st.sidebar.button(example, key=f"ex_{example}", use_container_width=True):
            # Store the question to process
            st.session_state.pending_question = example
            st.rerun()