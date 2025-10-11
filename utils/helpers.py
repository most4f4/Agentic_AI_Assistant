"""
Utility helper functions
"""
from typing import List, Dict


def count_messages_by_role(messages: List[Dict[str, str]]) -> Dict[str, int]:
    """
    Count messages by role
    
    Args:
        messages: List of message dictionaries with 'role' key
        
    Returns:
        Dictionary with counts for each role
    """
    counts = {}
    for message in messages:
        role = message.get("role", "unknown")
        counts[role] = counts.get(role, 0) + 1
    return counts


def get_file_extension(filename: str) -> str:
    """
    Extract file extension from filename
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension in lowercase
    """
    return filename.split(".")[-1].lower() if "." in filename else ""


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length of the text
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def generate_session_title(first_message: str, max_words: int = 4) -> str:
    """
    Generate a smart session title from the first message
    
    Args:
        first_message: The first user message
        max_words: Maximum number of words in title
        
    Returns:
        A concise session title
    """
    # Remove common question words
    stop_words = {"what", "how", "when", "where", "why", "who", "is", "are", "the", "a", "an", "can", "you", "please", "tell", "me"}
    
    # Split into words and clean
    words = first_message.lower().split()
    
    # Filter out stop words and get meaningful words
    meaningful_words = [w.strip("?.,!") for w in words if w.strip("?.,!") not in stop_words]
    
    # Take first max_words meaningful words
    title_words = meaningful_words[:max_words] if meaningful_words else words[:max_words]
    
    # Capitalize first letter of each word
    title = " ".join(word.capitalize() for word in title_words)
    
    # Truncate if too long
    if len(title) > 30:
        title = title[:27] + "..."
    
    return title or "New Chat"