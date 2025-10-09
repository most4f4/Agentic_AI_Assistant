"""
Document query tool for RAG-based question answering
"""
import streamlit as st
from langchain.tools import tool
from langchain.pydantic_v1 import BaseModel, Field


class DocumentQueryInput(BaseModel):
    query: str = Field(description="The question to ask about the uploaded documents")


@tool(args_schema=DocumentQueryInput)
def query_documents(query: str) -> str:
    """Search and answer questions from uploaded documents. 
    Use this tool when the user asks questions about their uploaded files or documents.
    This tool has access to the content of any PDFs, Word docs, or text files the user has uploaded."""
    try:
        # Check if RAG system is available
        if "rag_chain" not in st.session_state or st.session_state.rag_chain is None:
            return "No documents have been uploaded yet. Please upload a document first using the sidebar."
        
        # Query the RAG system
        result = st.session_state.rag_chain.invoke({"input": query})
        return result["answer"]
    except Exception as e:
        return f"Error querying documents: {e}"