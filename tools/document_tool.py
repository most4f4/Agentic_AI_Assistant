"""
Document query tool for RAG-based question answering with conversational support
"""
import streamlit as st
from langchain.tools import tool
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage



class DocumentQueryInput(BaseModel):
    query: str = Field(description="The question to ask about the uploaded documents")


@tool(args_schema=DocumentQueryInput)
def query_documents(query: str) -> str:
    """Search and answer questions from the user's uploaded documents (resume, CV, reports, PDFs, etc.).
    
    ALWAYS use this tool when the user asks about:
    - Their resume, CV, work experience, education, skills, or job history
    - Their uploaded documents, files, or PDFs
    - Information "in my document", "in my file", "in my resume"
    - Personal information like "my job", "my experience", "my education"
    - Any question that requires reading uploaded content
    
    This tool has access to ALL uploaded PDFs, Word docs, and text files.
    It supports conversational context, so follow-up questions work correctly.
    
    Before saying you don't have access to user data, CHECK if documents are uploaded and use this tool first."""
    try:
        # Check if RAG system is available
        if "rag_chain" not in st.session_state or st.session_state.rag_chain is None:
            return "No documents have been uploaded yet. Please upload a document first using the sidebar."
        
        # Get chat history for conversational context
        chat_history = get_rag_chat_history()
        
        # Query the RAG system with chat history
        result = st.session_state.rag_chain.invoke({
            "input": query,
            "chat_history": chat_history
        })
        answer = result["answer"]
        
        # Update chat history
        update_rag_chat_history(query, answer)
        
        return answer
    except Exception as e:
        return f"Error querying documents: {e}"
    


def get_rag_chat_history():
    """
    Get chat history for RAG in the correct format
    
    Returns:
        List of message objects for RAG chain
    """
    if "rag_chat_history" not in st.session_state:
        st.session_state.rag_chat_history = []
    
    return st.session_state.rag_chat_history


def update_rag_chat_history(query: str, answer: str):
    """
    Update the RAG chat history with new interaction
    
    Args:
        query: User's question
        answer: AI's answer
    """
    if "rag_chat_history" not in st.session_state:
        st.session_state.rag_chat_history = []
    
    # Add user message and AI response to history
    st.session_state.rag_chat_history.append(HumanMessage(content=query))
    st.session_state.rag_chat_history.append(AIMessage(content=answer))
    
    # Keep only last 10 exchanges (20 messages) to avoid context overflow
    if len(st.session_state.rag_chat_history) > 20:
        st.session_state.rag_chat_history = st.session_state.rag_chat_history[-20:]