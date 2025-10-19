# Voice Input/Output Module Documentation

## Overview

The Voice I/O module adds speech-to-text (STT) and text-to-speech (TTS) capabilities to your AI Assistant, powered by OpenAI's Whisper and TTS APIs. Users can speak their questions and hear AI responses in natural-sounding voices.

---

## Architecture

### Component Structure

```
project/
├── utils/
│   ├── voice_utils.py          # Core voice processing functions
│   └── __init__.py             # Exports voice functions
├── ui/
│   └── chat.py                 # Voice-enabled chat interface
├── config/
│   └── settings.py             # Voice configuration
└── requirements.txt            # Dependencies
```

---

## Core Components

### 1. **Voice Utilities (`utils/voice_utils.py`)**

This module contains all voice processing logic.

#### Functions:

##### `get_openai_client()`
- **Purpose**: Creates and returns an OpenAI client instance
- **Requirements**: `OPENAI_API_KEY` environment variable
- **Returns**: OpenAI client object
- **Error Handling**: Raises ValueError if API key is missing

```python
client = get_openai_client()
```

##### `speech_to_text_whisper(audio_bytes: bytes) -> str`
- **Purpose**: Converts spoken audio to text using OpenAI Whisper
- **Input**: Audio data in bytes (WAV format from recorder)
- **Output**: Transcribed text string
- **Process**:
  1. Saves audio bytes to temporary file (required by Whisper API)
  2. Sends file to Whisper API with language hint
  3. Receives transcription
  4. Cleans up temporary file
  5. Returns text or error message

**API Details**:
- Model: `whisper-1`
- Language: `en` (configurable)
- Response format: `text`
- Cost: ~$0.006 per minute of audio

**Error Messages**:
- `❌ Whisper transcription error: {details}` - API or processing error

##### `text_to_speech_openai(text: str, voice: str = "alloy") -> bytes`
- **Purpose**: Converts text to natural speech audio
- **Input**: 
  - `text`: String to speak
  - `voice`: Voice personality (alloy/echo/fable/onyx/nova/shimmer)
- **Output**: MP3 audio bytes
- **Process**:
  1. Sends text to OpenAI TTS API
  2. Receives MP3 audio stream
  3. Returns audio bytes

**API Details**:
- Model: `tts-1` (faster) or `tts-1-hd` (higher quality)
- Voices available: 6 personalities
- Response format: MP3
- Cost: $15 per 1M characters (tts-1), $30 per 1M (tts-1-hd)

##### `autoplay_audio(audio_bytes: bytes, format: str = "mp3")`
- **Purpose**: Auto-plays audio in the browser
- **Input**: Audio bytes and format
- **Output**: None (plays audio)
- **Process**:
  1. Encodes audio to base64
  2. Creates HTML `<audio>` element with autoplay
  3. Injects into Streamlit UI

**Technical Note**: Uses `unsafe_allow_html=True` to render HTML audio player

##### `get_available_voices() -> dict`
- **Purpose**: Returns available voice options with descriptions
- **Output**: Dictionary of voice names and characteristics

```python
{
    "alloy": "Neutral and balanced",
    "echo": "Clear and articulate",
    "fable": "Warm and expressive",
    "onyx": "Deep and authoritative",
    "nova": "Energetic and friendly",
    "shimmer": "Soft and calm"
}
```

---

### 2. **Chat Interface (`ui/chat.py`)**

Enhanced chat interface with voice controls.

#### Key Additions:

##### Voice Control Header
```python
col1, col2, col3 = st.columns([2, 1, 1])
with col2:
    voice_enabled = st.toggle("🎤 Voice", ...)
with col3:
    auto_speak = st.toggle("🔊 Auto-speak", ...)
```

**Session State Variables**:
- `voice_enabled`: Boolean - Master toggle for voice features
- `auto_speak`: Boolean - Auto-play AI responses
- `selected_voice`: String - Current TTS voice selection

##### Per-Message Read Aloud
```python
if message["role"] == "assistant" and voice_enabled:
    if st.button("🔊", key=f"tts_{i}"):
        audio_bytes = text_to_speech_openai(message["content"])
        autoplay_audio(audio_bytes)
```

Adds a speaker button to every AI response for manual playback.

##### Voice Input Section
When `voice_enabled=True`, displays:
1. **Voice selector dropdown** - Choose TTS voice
2. **Audio recorder widget** - Click to record
3. **Preview expander** - Review recording
4. **Transcription display** - Show what you said
5. **Send button** - Submit transcribed message

**Flow**:
```
User clicks mic → Records audio → Stops recording
    ↓
Audio saved to session state
    ↓
Display preview player
    ↓
Call speech_to_text_whisper(audio_bytes)
    ↓
Show transcription with success message
    ↓
User clicks "Send this message"
    ↓
Process as normal chat input
```

##### Auto-Speak Response
```python
if auto_speak:
    voice = st.session_state.get("selected_voice", "alloy")
    audio_bytes = text_to_speech_openai(answer, voice=voice)
    if audio_bytes:
        autoplay_audio(audio_bytes)
```

Automatically speaks AI responses when enabled.

---

### 3. **Configuration (`config/settings.py`)**

```python
VOICE_CONFIG = {
    "enabled": True,              # Master enable/disable
    "default_voice": "alloy",     # Default TTS voice
    "tts_model": "tts-1",         # Speed vs quality
    "auto_speak": True,           # Auto-play responses
    "whisper_language": "en",     # STT language hint
}
```

**Configuration Options**:

| Setting | Options | Description |
|---------|---------|-------------|
| `enabled` | True/False | Global voice feature toggle |
| `default_voice` | alloy/echo/fable/onyx/nova/shimmer | Default TTS personality |
| `tts_model` | tts-1 / tts-1-hd | Speed (tts-1) vs Quality (tts-1-hd) |
| `auto_speak` | True/False | Auto-play AI responses |
| `whisper_language` | ISO code | Language hint for better accuracy |

---

## User Workflow

### Voice Input Flow

```
┌─────────────────────────────────────────┐
│ 1. User toggles "🎤 Voice" ON          │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 2. Voice input section appears          │
│    - Microphone button shown            │
│    - Voice selector dropdown shown      │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 3. User clicks microphone button        │
│    - Recorder starts (red indicator)    │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 4. User speaks their question           │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 5. User clicks to stop recording        │
│    - Audio saved as WAV bytes           │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 6. Audio preview player appears         │
│    - User can replay their recording    │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 7. Whisper transcription starts         │
│    - "🎤 Transcribing..." spinner shown │
│    - API call to OpenAI Whisper         │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 8. Transcription displayed               │
│    - Green success box                   │
│    - "📝 You said: [text]"               │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 9. "✅ Send this message" button shown  │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 10. User clicks send                     │
│     - Processes like text input          │
│     - Agent generates response           │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 11. AI response displayed                │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 12. If Auto-speak ON:                    │
│     - TTS API called automatically       │
│     - Response spoken aloud              │
└─────────────────────────────────────────┘
```

### Voice Output Flow (Manual)

```
┌─────────────────────────────────────────┐
│ 1. AI response displayed in chat        │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 2. If voice enabled:                     │
│    - 🔊 button appears next to message  │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 3. User clicks 🔊 button                │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 4. "Generating speech..." spinner       │
│    - TTS API call with selected voice   │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 5. Audio auto-plays in browser          │
│    - HTML audio element with autoplay   │
└─────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
┌─────────────────┐
│  User's Voice   │
└────────┬────────┘
         │
         ↓ (Microphone captures)
┌─────────────────────────┐
│ audio-recorder-streamlit│
│   (Browser WebRTC API)  │
└────────┬────────────────┘
         │
         ↓ (WAV bytes)
┌─────────────────────────┐
│ speech_to_text_whisper()│
│   - Save to temp file   │
│   - Call Whisper API    │
│   - Clean up temp file  │
└────────┬────────────────┘
         │
         ↓ (Text string)
┌─────────────────────────┐
│   Streamlit Display     │
│ "📝 You said: [text]"   │
└────────┬────────────────┘
         │
         ↓ (User confirms)
┌─────────────────────────┐
│  _process_user_input()  │
│   - Add to messages     │
│   - Build chat history  │
│   - Call agent          │
└────────┬────────────────┘
         │
         ↓ (AI response)
┌─────────────────────────┐
│  Display AI Response    │
└────────┬────────────────┘
         │
         ↓ (If auto_speak=True)
┌─────────────────────────┐
│ text_to_speech_openai() │
│   - Call TTS API        │
│   - Get MP3 bytes       │
└────────┬────────────────┘
         │
         ↓ (MP3 bytes)
┌─────────────────────────┐
│    autoplay_audio()     │
│   - Base64 encode       │
│   - Create HTML audio   │
│   - Inject to page      │
└────────┬────────────────┘
         │
         ↓ (Browser plays)
┌─────────────────────────┐
│   User Hears Response   │
└─────────────────────────┘
```

---

## Technical Details

### Audio Formats

**Input (Recording)**:
- Format: WAV
- Captured by: `audio-recorder-streamlit`
- Source: Browser's WebRTC API (MediaRecorder)
- Sent to: Whisper API (requires file upload)

**Output (Playback)**:
- Format: MP3
- Generated by: OpenAI TTS API
- Delivery: Base64-encoded in HTML audio element
- Playback: Browser's native audio player

### Session State Management

```python
# Voice-related session state
st.session_state.voice_enabled = False      # Voice toggle state
st.session_state.auto_speak = True          # Auto-speak toggle
st.session_state.selected_voice = "alloy"   # Current voice selection
```

These persist across Streamlit reruns, maintaining user preferences.

### Error Handling

**Speech-to-Text Errors**:
```python
if transcribed_text.startswith("❌"):
    st.error(transcribed_text)  # Show error in UI
    # User can retry recording
```

**Text-to-Speech Errors**:
```python
if audio_bytes is None:
    # Error already displayed via st.error in function
    # Gracefully continue without audio
```

### API Rate Limits

**Whisper API**:
- File size limit: 25 MB
- Typical 30-second recording: ~500 KB
- No explicit rate limit, uses OpenAI account limits

**TTS API**:
- Character limit per request: ~4096 tokens
- Typical AI response: 200-500 tokens
- Rate limit: Based on OpenAI tier (default: 500 RPM)

---

## Cost Analysis

### Per Interaction Estimate

**Typical Voice Query** (30 seconds):
- Whisper transcription: $0.003
- AI response generation (gpt-4o): $0.01-0.05
- TTS playback (200 words): $0.003
- **Total**: ~$0.016-0.056 per voice interaction

### Monthly Usage Example

**100 voice interactions/month**:
- Whisper: $0.30
- TTS: $0.30
- AI generation: $1.00-5.00
- **Total**: ~$1.60-5.60/month

**Optimization Tips**:
- Use `tts-1` instead of `tts-1-hd` (50% cost savings)
- Disable auto-speak for cost control
- Keep responses concise

---

## Dependencies

```txt
# Core voice functionality
openai>=1.0.0                    # Whisper & TTS APIs
audio-recorder-streamlit>=0.0.8  # Browser microphone access

# Already in project (required)
streamlit>=1.28.0                # UI framework
python-dotenv>=1.0.0             # Environment variables
```

### Browser Requirements

- **WebRTC support** (all modern browsers)
- **HTTPS required** for microphone access (or localhost)
- **Microphone permissions** must be granted

---

## Security Considerations

### API Key Protection
```python
# NEVER commit to git
OPENAI_API_KEY=sk-your-key-here
```

Always use environment variables, never hardcode.

### Audio Data Privacy
- Audio bytes stay in session memory
- Temporary files deleted immediately after processing
- No audio stored permanently (unless explicitly saved)
- OpenAI processes audio per their privacy policy

### HTTPS Requirement
- Browser blocks microphone on HTTP (except localhost)
- Deploy with SSL certificate for production

---

## Troubleshooting

### Common Issues

#### 1. "Microphone not found"
**Cause**: Browser doesn't have mic permissions  
**Solution**: 
- Check browser permissions
- Ensure HTTPS (or localhost)
- Try different browser

#### 2. "OPENAI_API_KEY not found"
**Cause**: Environment variable not set  
**Solution**:
```bash
# Add to .env file
OPENAI_API_KEY=sk-your-key-here
```

#### 3. "Whisper transcription error: Rate limit"
**Cause**: Too many API requests  
**Solution**:
- Wait and retry
- Upgrade OpenAI tier
- Implement request throttling

#### 4. "Audio doesn't play"
**Cause**: Browser autoplay policy  
**Solution**:
- User must interact with page first
- Check browser console for errors
- Ensure audio format supported

#### 5. "Poor transcription quality"
**Cause**: Background noise or unclear speech  
**Solution**:
- Speak clearly and slowly
- Use better microphone
- Add language hint in config

---

## Future Enhancements

### Potential Improvements

1. **Multi-language Support**
   - Detect language automatically
   - Support 99+ languages Whisper supports

2. **Voice Commands**
   - "Clear chat", "New session", etc.
   - Wake word detection

3. **Streaming TTS**
   - Stream audio as it's generated
   - Reduce latency

4. **Voice Cloning**
   - Custom voice profiles
   - User-specific voices

5. **Offline Mode**
   - Local Whisper model
   - Fallback speech recognition

6. **Audio Effects**
   - Speed control
   - Pitch adjustment
   - Background music

---

## API Reference Quick Guide

### Whisper API
```python
client.audio.transcriptions.create(
    model="whisper-1",           # Only available model
    file=audio_file,             # File object (required)
    language="en",               # Optional ISO 639-1 code
    response_format="text"       # text/json/srt/vtt/verbose_json
)
```

### TTS API
```python
client.audio.speech.create(
    model="tts-1",               # tts-1 or tts-1-hd
    voice="alloy",               # 6 voices available
    input=text,                  # Text to speak
    response_format="mp3"        # mp3/opus/aac/flac
)
```

---

## Testing Checklist

- [ ] Voice toggle enables/disables features
- [ ] Auto-speak toggle works correctly
- [ ] All 6 voices can be selected
- [ ] Microphone records audio properly
- [ ] Whisper transcribes accurately
- [ ] Manual read-aloud buttons work
- [ ] Auto-speak plays responses
- [ ] Text input still works with voice enabled
- [ ] Voice works with uploaded documents
- [ ] Error messages display correctly
- [ ] Session state persists across reruns
- [ ] Cost stays within budget

---

## Maintenance Notes

### Regular Checks
- Monitor OpenAI API usage dashboard
- Check for `audio-recorder-streamlit` updates
- Review OpenAI model deprecations
- Test across different browsers

### Version Updates
- OpenAI library updates may change API
- Streamlit updates may affect audio playback
- Browser policy changes may affect WebRTC

---

## Summary

The voice module transforms your AI assistant into a conversational interface using industry-leading speech recognition (Whisper) and natural text-to-speech. The modular design keeps voice logic separate from core chat functionality, making it easy to maintain, test, and extend.

**Key Benefits**:
- ✅ Hands-free interaction
- ✅ Accessibility for users who prefer speaking
- ✅ Natural-sounding AI voices
- ✅ High accuracy transcription
- ✅ Seamless integration with existing chat
- ✅ Configurable and extensible

**Architecture Principles**:
- Separation of concerns (voice logic isolated)
- Session state for user preferences
- Graceful error handling
- Cost-conscious design
- Browser-native audio handling
