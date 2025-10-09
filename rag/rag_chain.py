"""
RAG chain creation and management
"""
import os
import tempfile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from config.settings import RAG_CONFIG
from .document_loader import load_document


def process_documents(uploaded_files):
    """
    Process uploaded files and create a RAG chain
    
    Args:
        uploaded_files: List of uploaded file objects from Streamlit
        
    Returns:
        RAG chain object or None if processing fails
    """
    all_documents = []
    
    # Process each uploaded file
    for uploaded_file in uploaded_files:
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Determine file type
        file_extension = uploaded_file.name.split(".")[-1].lower()
        
        # Load document
        documents = load_document(tmp_file_path, file_extension)
        
        if documents:
            all_documents.extend(documents)
        
        # Clean up temp file
        os.unlink(tmp_file_path)
    
    if not all_documents:
        return None
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=RAG_CONFIG["chunk_size"],
        chunk_overlap=RAG_CONFIG["chunk_overlap"]
    )
    splits = text_splitter.split_documents(all_documents)
    
    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings(model=RAG_CONFIG["embedding_model"])
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        collection_name=RAG_CONFIG["collection_name"]
    )
    
    # Create retriever
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": RAG_CONFIG["retriever_k"]}
    )
    
    # Create QA chain
    llm = ChatOpenAI(model="gpt-4o")
    
    qa_system_prompt = (
        "You are an assistant for question-answering tasks. Use "
        "the following pieces of retrieved context to answer the "
        "question. If you don't know the answer, just say that you "
        "don't know. Keep the answer concise and accurate."
        "\n\n"
        "{context}"
    )
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return rag_chain