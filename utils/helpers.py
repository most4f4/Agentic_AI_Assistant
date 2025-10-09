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