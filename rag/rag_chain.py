"""
RAG chain creation and management
"""
import os
import tempfile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

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
        search_type="similarity_score_threshold",
        search_kwargs={"k": RAG_CONFIG["retriever_k"], "score_threshold": RAG_CONFIG["similarity_score_threshold"]}
    )
    
    # Create QA chain
    llm = ChatOpenAI(model="gpt-4o")

    # Contextualize question prompt
    # This helps the LLM reformulate follow-up questions using chat history
    # Example: "Tell me more about it" → "Tell me more about AI ethics"
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, just "
        "reformulate it if needed and otherwise return it as is."
    )
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    # Create history-aware retriever
    # This retriever reformulates questions based on chat history before searching
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    
    # Answer question prompt with chat history
    qa_system_prompt = (
    "You are a helpful assistant answering questions about the user's uploaded documents. "
    "Use the context below to provide accurate answers.\n\n"
    
    "Guidelines:\n"
    "- Answer based on the provided context\n"
    "- If information is in the context, provide it with confidence and detail\n"
    "- If context is partial, answer what you can and explain what's missing\n"
    "- If context doesn't contain the answer, say so clearly\n"
    "- Reference conversation history to understand follow-up questions\n"
    "- Be natural and conversational, not robotic\n\n"
    
    "{context}"
)
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    # Create question-answer chain
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    
    # Create final conversational RAG chain
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    return rag_chain