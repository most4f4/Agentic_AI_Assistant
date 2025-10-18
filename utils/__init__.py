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

from .voice_utils import (
    speech_to_text_whisper,
    text_to_speech_openai,
    autoplay_audio,
    get_available_voices
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
    'load_chat_from_cloud',
    'speech_to_text_whisper',
    'text_to_speech_openai',
    'autoplay_audio',
    'get_available_voices'
]