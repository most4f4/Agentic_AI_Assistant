"""
Firebase Firestore integration for chat history persistence
"""
import os
import streamlit as st
from google.cloud import firestore
from langchain_google_firestore import FirestoreChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime
from typing import List, Dict, Optional


class FirestoreManager:
    """Manages chat history persistence with Firebase Firestore"""

    def __init__(self, project_id: str, collection_name: str = "chat_sessions"):
        """
        Initialize Firestore Manager
        
        Args:
            project_id: Your Firebase project ID
            collection_name: Firestore collection name for storing chats
        """
        self.project_id = project_id
        self.collection_name = collection_name
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Firestore client"""
        try:
            # Check if credentials are set in environment variables
            if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                st.warning("⚠️ Firebase credentials not configured. Messages will not be saved to cloud.")
                return
            
            self.client = firestore.Client(project=self.project_id)
            st.success("✅ Connected to Firebase Firestore")
        except Exception as e:
            st.error(f"❌ Failed to connect to Firestore: {e}")
            self.client = None

    def is_connected(self) -> bool:
        """Check if Firestore is connected"""
        return self.client is not None\
        
    def get_chat_history(self, session_id: str) -> FirestoreChatMessageHistory:
        """
        Get chat history for a session
        
        Args:
            session_id: Unique identifier for the chat session (e.g., user ID or session UUID)
            
        Returns:
            FirestoreChatMessageHistory object
        """
        if not self.is_connected():
            return None
        
        return FirestoreChatMessageHistory(
            session_id=session_id,
            collection=self.collection_name,
            client=self.client,
        )
    
    def save_message(self, session_id: str, role: str, content: str):
        """
        Save a single message to Firestore
        
        Args:
            session_id: Unique session identifier
            role: 'user' or 'assistant'
            content: Message content
        """
        if not self.is_connected():
            st.warning("⚠️ Firestore not connected. Message not saved.")
            return
        
        try:
            chat_history = self.get_chat_history(session_id)
            if role == "user":
                chat_history.add_user_message(content)
            elif role == "assistant":
                chat_history.add_ai_message(content)
        except Exception as e:
            st.error(f"❌ Failed to save message: {e}")

    def save_messages_batch(self, session_id: str, messages: List[Dict[str, str]]):
        """
        Save multiple messages at once
        
        Args:
            session_id: Unique session identifier
            messages: List of message dicts with 'role' and 'content'
        """
        if not self.is_connected():
            st.warning("⚠️ Firestore not connected. Messages not saved.")
            return

        try:
            chat_history = self.get_chat_history(session_id)
            for msg in messages:
                if msg["role"] == "user":
                    chat_history.add_user_message(msg["content"])
                elif msg["role"] == "assistant":
                    chat_history.add_ai_message(msg["content"])
            st.success(f"✅ Saved {len(messages)} messages to Firestore")
        except Exception as e:
            st.error(f"❌ Failed to save messages: {e}")

    def load_messages(self, session_id: str) -> List[Dict[str, str]]:
        """
        Load messages from Firestore
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of message dictionaries
        """
        if not self.is_connected():
            return []
        
        try:
            chat_history = self.get_chat_history(session_id)
            messages = []

            for msg in chat_history.messages:
                if isinstance(msg, HumanMessage):
                    messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    messages.append({"role": "assistant", "content": msg.content})

            return messages
        except Exception as e:
            st.error(f"❌ Failed to load messages: {e}")
            return []
        
    
    def clear_session(self, session_id: str):
        """
        Clear all messages for a session
        
        Args:
            session_id: Unique session identifier
        """

        if not self.is_connected():
            st.warning("⚠️ Firestore not connected. Cannot clear session.")
            return
        
        try:
            chat_history = self.get_chat_history(session_id)
            chat_history.clear()
            st.success(f"✅ Cleared chat history for session {session_id}")
        except Exception as e:
            st.error(f"❌ Failed to clear session: {e}")


    def list_sessions(self, user_id: Optional[str] = None) -> List[str]:
        """
        List all session IDs (optionally filtered by user)
        
        Args:
            user_id: Optional user ID to filter sessions
            
        Returns:
            List of session IDs
        """

        if not self.is_connected():
            return []
        
        try:
            # Query Firestore for all documents in the collection
            sessions = self.client.collection(self.collection_name).stream()
            session_ids = [session.id for session in sessions]
            
            return session_ids
        except Exception as e:
            st.error(f"❌ Failed to list sessions: {e}")
            return []
        
    def get_session_metadata(self, session_id: str) -> Dict:
        """
        Get metadata about a session (message count, created date, etc.)
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Dictionary with session metadata
        """
        if not self.is_connected():
            return {}
        
        try:
            chat_history = self.get_chat_history(session_id)
            messages = chat_history.messages
            
            return {
                "session_id": session_id,
                "message_count": len(messages),
                "has_messages": len(messages) > 0,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            st.error(f"❌ Failed to get session metadata: {e}")
            return {}
        

# Convenience functions for Streamlit
def init_firestore(project_id: str) -> FirestoreManager:
    """
    Initialize Firestore manager and store in session state
    
    Args:
        project_id: Firebase project ID
        
    Returns:
        FirestoreManager instance
    """
    if "firestore_manager" not in st.session_state:
        st.session_state.firestore_manager = FirestoreManager(project_id)

    return st.session_state.firestore_manager


def save_current_chat(session_id: str):
    """
    Save current chat from session state to Firestore
    
    Args:
        session_id: Session identifier
    """

    if "firestore_manager" in st.session_state and st.session_state.firestore_manager.is_connected():
        firestore_manager = st.session_state.firestore_manager
        messages = st.session_state.get("messages", [])
        
        if messages:
            firestore_manager.save_messages_batch(session_id, messages)


def load_chat_from_cloud(session_id: str):
    """
    Load chat from Firestore into session state
    
    Args:
        session_id: Session identifier
    """
    if "firestore_manager" in st.session_state and st.session_state.firestore_manager.is_connected():
        firestore_manager = st.session_state.firestore_manager
        messages = firestore_manager.load_messages(session_id)
        
        if messages:
            st.session_state.messages = messages
            st.success(f"✅ Loaded {len(messages)} messages from cloud")
        else:
            st.info("No messages found in cloud for this session")