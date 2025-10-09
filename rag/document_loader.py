"""
Document loading utilities for different file types
"""
import streamlit as st
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader
)


def load_document(file_path: str, file_type: str):
    """
    Load a document based on its type
    
    Args:
        file_path: Path to the document file
        file_type: Type of file (pdf, txt, docx, doc)
        
    Returns:
        List of document objects or None if loading fails
    """
    try:
        if file_type == "pdf":
            loader = PyPDFLoader(file_path)
        elif file_type == "txt":
            loader = TextLoader(file_path)
        elif file_type in ["docx", "doc"]:
            loader = UnstructuredWordDocumentLoader(file_path)
        else:
            return None
        
        documents = loader.load()
        return documents
    except Exception as e:
        st.error(f"Error loading document: {e}")
        return None