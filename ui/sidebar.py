"""
Sidebar UI components
"""
import uuid
import streamlit as st
from config.settings import TOOL_DESCRIPTIONS, EXAMPLE_QUESTIONS, SUPPORTED_FILE_TYPES, FIRESTORE_CONFIG
from rag.rag_chain import process_documents
from utils.firestore_manager import init_firestore, load_chat_from_cloud


def render_sidebar():
    """Render the complete sidebar with all components"""
    
    # Title and description
    st.sidebar.title("🛠️ Agent Tools")
    st.sidebar.markdown(TOOL_DESCRIPTIONS)
    st.sidebar.markdown("---")

    # Document upload section
    _render_document_upload()

    st.sidebar.markdown("---")
    
    # Cloud storage section (if enabled) - Show first for session management
    if FIRESTORE_CONFIG["enabled"]:
        _render_cloud_storage()
        st.sidebar.markdown("---")
    
    
    # Clear/New chat buttons
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.sidebar.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.rag_chat_history = []
            st.rerun()
    
    with col2:
        if st.sidebar.button("➕ New Chat", use_container_width=True):
            # Create new session
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.rag_chat_history = []
            st.session_state.session_name = None
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Example questions
    _render_example_questions()


def _render_cloud_storage():
    """Render cloud storage controls"""
    st.sidebar.subheader("☁️ Chat History")

    # Initialize Firestore if not already done
    if "firestore_manager" not in st.session_state:
        firestore_manager = init_firestore(FIRESTORE_CONFIG["project_id"])
        st.session_state.firestore_manager = firestore_manager

    firestore_manager = st.session_state.firestore_manager

    # Show connection status (compact)
    if not firestore_manager.is_connected():
        st.sidebar.error("❌ Not connected")
        st.sidebar.info("💡 Set GOOGLE_APPLICATION_CREDENTIALS in .env")
        return

    # Session ID management
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "session_name" not in st.session_state:
        st.session_state.session_name = None

    # Auto-save toggle (compact)
    auto_save = st.sidebar.checkbox(
        "💾 Auto-save", 
        value=FIRESTORE_CONFIG.get("auto_save", True),
        help="Automatically save conversations to cloud"
    )
    st.session_state.auto_save_enabled = auto_save

    # List previous sessions (ChatGPT style)
    _render_session_list(firestore_manager)


def _render_session_list(firestore_manager):
    """Render session list like ChatGPT with lazy loading"""
    
    # Get all session IDs (fast - just IDs, no content)
    sessions = firestore_manager.list_sessions()
    
    if not sessions:
        st.sidebar.info("No saved chats yet")
        return
    
    st.sidebar.markdown("**💬 Previous Chats**")

    # Cache session metadata to avoid repeated queries
    if "session_cache" not in st.session_state:
        st.session_state.session_cache = {}
    
    # Get session titles (only metadata, not full messages)
    session_data = []
    for session_id in sessions[-10:]:  # Only last 10 sessions
        # Check cache first
        if session_id in st.session_state.session_cache:
            session_data.append(st.session_state.session_cache[session_id])
        else:
            # Get metadata (includes stored title)
            metadata = firestore_manager.get_session_metadata(session_id)
            if metadata:
                title = metadata.get("title", "New Chat")  # Just read title
                
                session_info = {
                    "id": session_id,
                    "title": title,
                    "message_count": metadata.get("message_count", 0)
                }
                
                # Cache it
                st.session_state.session_cache[session_id] = session_info
                session_data.append(session_info)
    
    # Reverse to show newest first
    session_data.reverse()
    
    # Display sessions
    for session in session_data:
        # Highlight current session
        is_current = session["id"] == st.session_state.session_id
        icon = "💬" if is_current else "📝"

        # Create columns for session name and delete button
        col1, col2 = st.sidebar.columns([4, 1])
        
        with col1:
            button_label = f"{icon} {session['title']}"
            if st.button(
                button_label, 
                key=f"session_{session['id']}", 
                use_container_width=True,
                type="primary" if is_current else "secondary"
            ):
                if not is_current:
                    with st.spinner(f"Loading {session['title']}..."):
                        st.session_state.session_id = session["id"]
                        st.session_state.session_name = session["title"]
                        load_chat_from_cloud(session["id"])
                    st.rerun()
    
        with col2:  
            if st.button("🗑️", key=f"del_{session['id']}", help="Delete chat"):
                firestore_manager.clear_session(session["id"])
                # Clear from cache
                if session["id"] in st.session_state.session_cache:
                    del st.session_state.session_cache[session["id"]]
                # If deleting current session, create new one
                if session["id"] == st.session_state.session_id:
                    st.session_state.session_id = str(uuid.uuid4())
                    st.session_state.messages = []
                    st.session_state.rag_chat_history = []
                st.rerun()


def _render_document_upload():
    """Render the document upload section"""
    st.sidebar.subheader("📁 Upload Documents")

    # Show status if documents are loaded
    if st.session_state.get('rag_chain') is not None:
        st.sidebar.success("✅ Documents loaded!")
    else:
        st.sidebar.info("📤 Upload files")
    
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
        if current_files != st.session_state.get('uploaded_files_names', []):
            with st.sidebar:
                with st.spinner("Processing..."):
                    rag_chain = process_documents(uploaded_files)
                    if rag_chain:
                        st.session_state.rag_chain = rag_chain
                        st.session_state.uploaded_files_names = current_files
                        st.session_state.rag_chat_history = []
                        st.success(f"✅ {len(uploaded_files)} file(s) ready!")
                    else:
                        st.error("Failed to process")
        
        # Show uploaded files (compact)
        with st.sidebar.expander(f"📄 {len(uploaded_files)} file(s)"):
            for file in uploaded_files:
                st.text(file.name)
    else:
        st.session_state.rag_chain = None
        st.session_state.uploaded_files_names = []
        st.session_state.rag_chat_history = []


def _render_example_questions():
    """Render example questions as buttons"""
    st.sidebar.markdown("**💡 Try asking:**")
    
    for example in EXAMPLE_QUESTIONS:
        if st.sidebar.button(example, key=f"ex_{example}", use_container_width=True):
            st.session_state.pending_question = example
            st.rerun()