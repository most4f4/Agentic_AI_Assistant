"""
Voice input/output utilities for AI Assistant using OpenAI
"""
import os
import tempfile
import io
import streamlit as st
from openai import OpenAI

def get_openai_client():
    """Initialize and return OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    return OpenAI(api_key=api_key)


def speech_to_text_whisper(audio_bytes: bytes) -> str:
    """
    Convert speech to text using OpenAI Whisper API
    
    Args:
        audio_bytes: Audio data in bytes
        
    Returns:
        Transcribed text or error message
    """
    try:
        client = get_openai_client()
        # Save audio to temp file (Whisper API requires a file)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
            temp_audio_file.write(audio_bytes)
            temp_audio_file_path = temp_audio_file.name

        # Transcribe using Whisper
        with open(temp_audio_file_path, "rb") as audio_file: # "rb" for read binary
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                language="en",
                model="whisper-1",
                response_format="text"
            )

        # Clean up temp file
        os.remove(temp_audio_file_path)

        return transcription if isinstance(transcription, str) else transcription.text
    
    except Exception as e:
        return f"❌ Whisper transcription error: {str(e)}"
    

def text_to_speech_openai(text: str, voice: str = "alloy") -> bytes:
    """
    Convert text to speech using OpenAI TTS API
    
    Args:
        text: Text to convert to speech
        voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
        
    Returns:
        Audio data in bytes
    """
    try:
        client = get_openai_client()

        tts_response = client.audio.speech.create(
            model="tts-1", # Use "tts-1-hd" for higher quality (costs more)
            voice=voice,
            input=text,
            response_format="mp3"
        )

        return tts_response.content
    
    except Exception as e:
        st.error(f"❌ OpenAI TTS error: {str(e)}")
        return None
    
def autoplay_audio(audio_bytes: bytes, format: str = "mp3"):
    """
    Auto-play audio in Streamlit using HTML audio player
    
    Args:
        audio_bytes: Audio data in bytes
        format: Audio format (mp3, wav, etc.)
    """
    import base64
    # Convert to base64
    audio_base64 = base64.b64encode(audio_bytes).decode()

    # Create HTML audio element with autoplay
    audio_html = f"""
    <audio autoplay>
        <source src="data:audio/{format};base64,{audio_base64}" type="audio/{format}">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

def get_available_voices():
    """
    Get list of available OpenAI TTS voices
    
    Returns:
        List of voice names with descriptions
    """
    return {
        "alloy": "Neutral and balanced",
        "echo": "Clear and articulate",
        "fable": "Warm and expressive",
        "onyx": "Deep and authoritative",
        "nova": "Energetic and friendly",
        "shimmer": "Soft and calm"
    }

