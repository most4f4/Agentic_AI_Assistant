"""
Configuration settings for the AI Assistant
"""

# Streamlit page configuration
PAGE_CONFIG = {
    "page_title": "AI Assistant with RAG",
    "page_icon": "🤖",
    "layout": "wide"
}

# LLM Configuration
LLM_CONFIG = {
    "model": "gpt-4o",
}

# Agent Configuration
AGENT_CONFIG = {
    "verbose": True,
    "handle_parsing_errors": True,
    "max_iterations": 5,
}

# RAG Configuration
RAG_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "embedding_model": "text-embedding-3-small",
    "retriever_k": 3,
    "collection_name": "uploaded_docs"
}

# Firestore Configuration (optional - for cloud storage)
FIRESTORE_CONFIG = {
    "enabled": True,  # Set to True to enable cloud storage
    "project_id": "ai-assistant-25549",  # Replace with your Firebase project ID
    "collection_name": "chat_sessions",
    "auto_save": True,  # Automatically save after each message
}

# Supported file types
SUPPORTED_FILE_TYPES = ["pdf", "txt", "docx", "doc"]

# Example questions for sidebar
EXAMPLE_QUESTIONS = [
    "What's the weather in Tokyo?",
    "Convert 100 USD to EUR",
    "What's the current price of AAPL stock?",
    "Calculate 245 * 67 + 891",
    "Search for the latest AI news",
    "What is this document about?",
    "Summarize the key points from my uploaded file"
]

# Tool descriptions for sidebar
TOOL_DESCRIPTIONS = """
The AI agent has access to these tools and will automatically choose which ones to use:

**Available Tools:**
- 🔍 **Web Search** - Search for current information
- 🌤️ **Weather** - Get weather for any city
- 💱 **Currency Converter** - Convert between currencies
- 📊 **Stock Prices** - Look up stock information
- 🧮 **Calculator** - Perform calculations
- 📄 **Document Q&A** - Answer questions from uploaded files

The agent will reason about your question and decide which tools to use!
"""