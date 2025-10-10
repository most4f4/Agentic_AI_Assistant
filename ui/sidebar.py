"""
Sidebar UI components
"""
import streamlit as st
from config.settings import TOOL_DESCRIPTIONS, EXAMPLE_QUESTIONS, SUPPORTED_FILE_TYPES
from rag.rag_chain import process_documents


def render_sidebar():
    """Render the complete sidebar with all components"""
    
    # Title and description
    st.sidebar.title("🛠️ Agent Tools")
    st.sidebar.markdown(TOOL_DESCRIPTIONS)
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


def _render_document_upload():
    """Render the document upload section"""
    st.sidebar.subheader("📁 Upload Documents")
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
                        st.success(f"✅ Processed {len(uploaded_files)} document(s)!")
                    else:
                        st.error("Failed to process documents")
        
        # Show uploaded files
        st.sidebar.markdown("**Uploaded Files:**")
        for file in uploaded_files:
            st.sidebar.text(f"📄 {file.name}")
    else:
        st.session_state.rag_chain = None
        st.session_state.uploaded_files_names = []


def _render_example_questions():
    """Render example questions as buttons"""
    st.sidebar.markdown("**💡 Try asking:**")
    
    for example in EXAMPLE_QUESTIONS:
        if st.sidebar.button(example, key=f"ex_{example}", use_container_width=True):
            # Store the question to process
            st.session_state.pending_question = example
            st.rerun()