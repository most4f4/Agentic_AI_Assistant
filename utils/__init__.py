"""Utils package - Utility functions"""
from .helpers import (
    count_messages_by_role,
    get_file_extension,
    truncate_text,
    format_file_size,
    generate_session_title
)

from .firestore_manager import (
        FirestoreManager,
        init_firestore,
        save_current_chat,
        load_chat_from_cloud
    )

__all__ = [
        'count_messages_by_role',
        'get_file_extension',
        'truncate_text',
        'format_file_size',
        'generate_session_title',
        'FirestoreManager',
        'init_firestore',
        'save_current_chat',
        'load_chat_from_cloud'
    ]