# 🤖 AI Assistant with RAG & Reasoning Agent

A powerful AI assistant built with LangChain and Streamlit that can reason about which tools to use, search the web, answer questions from uploaded documents, and perform various tasks autonomously with full conversational context awareness and **voice interaction capabilities**.

## ✨ Features

- **🧠 Reasoning Agent**: Uses GPT-4 to intelligently decide which tools to use
- **💬 Conversational Context**: Understands follow-up questions and pronouns ("it", "that", "there")
- **🎤 Voice Input/Output**: Speak to the AI and hear responses with natural voices (OpenAI Whisper & TTS)
- **📄 Document Q&A (RAG)**: Upload PDFs, Word docs, or text files and ask questions with conversation history
- **☁️ Cloud Storage**: Save conversations to Firebase Firestore for persistence across sessions
- **🔍 Web Search**: Search for current information and news
- **🌤️ Weather**: Get real-time weather for any city
- **💱 Currency Converter**: Convert between major currencies
- **📊 Stock Prices**: Look up current stock information
- **🧮 Calculator**: Perform mathematical calculations

## 🆕 What's New

### **🎤 Voice Interaction (NEW!)**

- **High-quality speech recognition** using OpenAI Whisper
- **Natural text-to-speech** with 6 different voice personalities
- **Auto-speak mode** for hands-free operation
- **Multi-language support** (99+ languages via Whisper)
- Example usage:
  ```
  1. Toggle "🎤 Voice" in the chat interface
  2. Click microphone and speak your question
  3. AI transcribes and responds
  4. Enable "🔊 Auto-speak" to hear responses automatically
  ```

### **Conversational AI**

- Agent remembers conversation context (last 5 exchanges)
- Understands follow-up questions naturally
- Example:
  ```
  You: "What's my job?"
  AI: "Senior Developer at Google"
  You: "How long was I there?"  ← Understands "there" = Google
  AI: "You worked there for 3 years"
  ```

### **Cloud Storage**

- Save conversations to Firebase Firestore
- Auto-save mode for automatic backup
- Resume conversations from any device
- Session management for multiple conversations
- Free tier supports 100+ users

## 📁 Project Structure

```
ai_assistant/
│
├── app.py                      # Main entry point
├── requirements.txt            # Dependencies
├── .env                        # API keys (create from .env.example)
├── .env.example                # Example environment variables
├── README.md                   # This file
├── docs/
│   ├── firebase_setup.md       # Cloud storage setup guide
│   └── voice_module.md         # Voice module comprehensive guide
│
├── config/
│   ├── __init__.py
│   └── settings.py            # Configuration settings (includes VOICE_CONFIG)
│
├── tools/
│   ├── __init__.py
│   ├── web_tools.py           # Web search
│   ├── weather_tool.py        # Weather lookup
│   ├── currency_tool.py       # Currency converter
│   ├── stock_tool.py          # Stock prices
│   ├── calculator_tool.py     # Calculator
│   └── document_tool.py       # Document Q&A (RAG)
│
├── agents/
│   ├── __init__.py
│   └── agent_setup.py         # Agent initialization
│
├── rag/
│   ├── __init__.py
│   ├── document_loader.py     # Document loading
│   └── rag_chain.py           # Conversational RAG chain
│
├── ui/
│   ├── __init__.py
│   ├── sidebar.py             # Enhanced sidebar with cloud controls
│   └── chat.py                # Chat interface with voice support
│
└── utils/
    ├── __init__.py
    ├── helpers.py             # Helper functions
    ├── firestore_manager.py   # Cloud storage manager
    └── voice_utils.py         # Voice input/output processing (NEW!)
```

## 🚀 Installation

### 1. Clone or Download the Project

```bash
# If using git
git clone <your-repo-url>
cd ai_assistant

# Or just download and extract the files
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API keys
```

Required API keys:

- **OpenAI API**: Get from [OpenAI Platform](https://platform.openai.com/api-keys) (Required for GPT-4, Embeddings, Whisper, and TTS)
- **Tavily API**: Get from [Tavily](https://tavily.com/) (For web search)
- **OpenWeather**: Get from [OpenWeatherMap](https://openweathermap.org/api) (For weather data)
- **SerpAPI**: Get from [SerpAPI](https://serpapi.com/) (For stock prices)
- **Firebase Firestore**: See [firebase_setup.md](docs/firebase_setup.md) for setup instructions

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🎯 Usage Examples

### Basic Queries

```
"What's the weather in Tokyo?"
"Convert 100 USD to EUR"
"What's the current price of AAPL stock?"
"Calculate 245 * 67 + 891"
"Search for the latest AI news"
```

### 🎤 Voice Interaction

1. **Enable Voice Mode**:

   - Toggle "🎤 Voice" in the chat interface
   - Optionally enable "🔊 Auto-speak" for automatic response playback

2. **Voice Input**:

   ```
   1. Click the microphone button
   2. Speak your question clearly
   3. Review the transcription
   4. Click "✅ Send this message"
   ```

3. **Voice Output**:

   - **Auto-speak**: Responses play automatically when enabled
   - **Manual**: Click 🔊 button next to any AI message

4. **Choose Your Voice**:
   - **Alloy**: Neutral and balanced (default)
   - **Echo**: Clear and articulate
   - **Fable**: Warm and expressive
   - **Onyx**: Deep and authoritative
   - **Nova**: Energetic and friendly
   - **Shimmer**: Soft and calm

### Conversational Follow-ups

```
You: "What's the weather in Paris?"
AI: "15°C, sunny"

You: "Convert 50 EUR to USD"  ← Understands Paris context
AI: "$54.50"

You: "What's the population?"  ← Knows you mean Paris
AI: "About 2.1 million"
```

### Document Q&A

1. Click "📁 Upload Documents" in the sidebar
2. Upload your PDF, Word, or text files
3. Ask questions with natural follow-ups:

   ```
   You: "What's my most recent job?"
   AI: "Senior Developer at Google"

   You: "Summarize it"  ← Understands "it" = the job
   AI: "As a Senior Developer at Google, you..."

   You: "What skills did I use there?"  ← Understands "there" = Google
   AI: "Python, TensorFlow, Cloud Computing..."
   ```

### Voice + Documents

You can use voice input to query your documents:

```
🎤 "What qualifications do I have?" (speaking)
AI: "You have a Master's degree in Computer Science..."

🎤 "Tell me more about that" (speaking)
AI: 🔊 "Your Master's degree was from MIT..." (speaking)
```

### Multi-Tool Queries

The agent can use multiple tools intelligently:

```
"What's the weather in Paris and how much is 50 EUR in USD?"
```

## ☁️ Cloud Storage

### Enable Cloud Storage

1. Follow the setup guide: [firebase_setup.md](docs/firebase_setup.md)
2. Update `config/settings.py`:
   ```python
   FIRESTORE_CONFIG = {
       "enabled": True,
       "project_id": "your-firebase-project-id",
       "auto_save": True,
   }
   ```
3. Restart the app

### Features

- **Auto-save**: Automatically backup each message
- **Session Management**: Multiple conversations
- **Multi-device**: Access from anywhere
- **Resume**: Continue conversations anytime

### Usage

- Click "💾 Auto-save" toggle to enable automatic backup
- Switch between sessions in "💬 Previous Chats"
- Click 🗑️ to delete individual sessions
- Click "➕ New Chat" to start fresh conversation

## 🛠️ Configuration

Edit `config/settings.py` to customize:

### LLM Model

```python
LLM_CONFIG = {
    "model": "gpt-4o",  # Change model here
}
```

### Voice Settings (NEW!)

```python
VOICE_CONFIG = {
    "enabled": True,              # Enable/disable voice features
    "default_voice": "alloy",     # Default TTS voice
    "tts_model": "tts-1",         # "tts-1" (faster) or "tts-1-hd" (quality)
    "auto_speak": True,           # Auto-play AI responses
    "whisper_language": "en",     # Language hint for Whisper
}
```

### RAG Settings

```python
RAG_CONFIG = {
    "chunk_size": 1000,        # Document chunk size
    "chunk_overlap": 200,      # Overlap between chunks
    "retriever_k": 3,          # Number of chunks to retrieve
}
```

### Agent Behavior

```python
AGENT_CONFIG = {
    "verbose": True,           # Show agent reasoning
    "max_iterations": 5,       # Max tool calls per query
}
```

### Cloud Storage

```python
FIRESTORE_CONFIG = {
    "enabled": False,          # Enable/disable cloud storage
    "project_id": "your-id",   # Firebase project ID
    "auto_save": True,         # Auto-save messages
    "auto_load": False,        # Auto-load last session on startup
}
```

## 📦 Adding New Tools

To add a new tool:

1. Create a new file in `tools/` (e.g., `tools/my_tool.py`)
2. Define your tool using the `@tool` decorator:

```python
from langchain.tools import tool
from langchain.pydantic_v1 import BaseModel, Field

class MyToolInput(BaseModel):
    input: str = Field(description="Input description")

@tool(args_schema=MyToolInput)
def my_tool(input: str) -> str:
    """Description of what your tool does"""
    # Your tool logic here
    return result
```

3. Import and add to `tools/__init__.py`
4. Add to the tools list in `agents/agent_setup.py`

## 🧪 Testing

### Test Individual Tools

```bash
# Test weather tool
python -c "from tools.weather_tool import get_weather; print(get_weather('London'))"

# Test calculator
python -c "from tools.calculator_tool import calculator; print(calculator('5 * 10 + 3'))"
```

### Test Voice Features

1. **Voice Input**:

   - Enable voice mode
   - Click microphone
   - Speak clearly: "What's the weather in Tokyo?"
   - Verify transcription accuracy

2. **Voice Output**:

   - Enable auto-speak
   - Ask any question
   - Verify audio plays correctly
   - Try different voices

3. **Voice + RAG**:
   - Upload a document
   - Use voice to ask: "What is this document about?"
   - Verify it uses query_documents tool

### Test Conversational Context

```
1. Ask: "What's the weather in Tokyo?"
2. Then: "Convert 100 JPY to USD"  ← Should understand Tokyo context
3. Then: "What's the population?"  ← Should understand you mean Tokyo
```

### Test Cloud Storage

```bash
# Test Firebase connection
python test_firestore.py
```

## 📝 API Keys Required

| Service        | Purpose                         | Get Key From                                             | Required |
| -------------- | ------------------------------- | -------------------------------------------------------- | -------- |
| OpenAI         | GPT-4, Embeddings, Whisper, TTS | [OpenAI Platform](https://platform.openai.com/)          | ✅ Yes   |
| Tavily         | Web Search                      | [Tavily](https://tavily.com/)                            | ✅ Yes   |
| OpenWeatherMap | Weather Data                    | [OpenWeatherMap](https://openweathermap.org/api)         | ✅ Yes   |
| SerpAPI        | Stock Prices                    | [SerpAPI](https://serpapi.com/)                          | ✅ Yes   |
| Firebase       | Cloud Storage                   | [Firebase Console](https://console.firebase.google.com/) | ✅ Yes   |

## 💰 Cost Considerations

### Voice Features Pricing

**OpenAI Whisper (Speech-to-Text)**:

- $0.006 per minute of audio
- Typical 30-second query: ~$0.003

**OpenAI TTS (Text-to-Speech)**:

- `tts-1`: $15 per 1M characters
- `tts-1-hd`: $30 per 1M characters
- Typical 200-word response: ~$0.003

**Estimated Monthly Cost** (100 voice interactions):

- Whisper: $0.30
- TTS: $0.30
- Total voice: **~$0.60/month**

**Cost Optimization Tips**:

- Use `tts-1` instead of `tts-1-hd` (50% savings)
- Disable auto-speak when not needed
- Keep responses concise

## 🎓 Key Concepts

### Conversational Agent

- Maintains chat history (last 10 messages)
- Understands pronouns and references
- Contextual tool selection

### Conversational RAG

- Document Q&A with memory
- Reformulates questions using history
- Separate RAG chat history (last 20 messages)

### Voice Processing

- **Speech-to-Text**: OpenAI Whisper (99+ languages)
- **Text-to-Speech**: OpenAI TTS (6 voices)
- **Auto-speak**: Optional hands-free mode
- See [voice_module.md](docs/voice_module.md) for technical details

### Two-Level Memory System

1. **Agent Memory**: For overall conversation and tool selection
2. **RAG Memory**: For document-specific follow-up questions

## 🤝 Contributing

Feel free to:

- Add new tools
- Improve existing features
- Fix bugs
- Enhance documentation
- Add tests
- Improve voice recognition accuracy

## 📄 License

MIT License - feel free to use this project for learning or commercial purposes.

## 🙏 Acknowledgments

Built with:

- [LangChain](https://python.langchain.com/) - Agent framework
- [Streamlit](https://streamlit.io/) - Web interface
- [OpenAI](https://openai.com/) - Language models, Whisper, TTS
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Firebase Firestore](https://firebase.google.com/docs/firestore) - Cloud storage
- [audio-recorder-streamlit](https://github.com/stefanrmmr/streamlit-audio-recorder) - Voice input component

## 📧 Support

If you encounter issues:

1. Check that all API keys are correctly set in `.env`
2. Verify all dependencies are installed (`pip install -r requirements.txt`)
3. Make sure you're using Python 3.8+
4. For cloud storage issues, see [firebase_setup.md](docs/firebase_setup.md)
5. For voice issues, see troubleshooting in [voice_module.md](docs/voice_module.md)

## ⚠️ Common Issues

### "Agent not using query_documents tool"

- Make sure documents are uploaded successfully
- Check for "✅ Documents loaded!" in sidebar
- Try more explicit questions: "Based on my uploaded resume, what's my job?"

### "Follow-up questions don't work"

- This is now fixed! The agent maintains conversation context
- If issues persist, check that `verbose=True` in settings to see agent reasoning

### "Cloud storage not connecting"

- Verify `GOOGLE_APPLICATION_CREDENTIALS` path in `.env`
- Check that Firebase API is enabled
- See troubleshooting section in [firebase_setup.md](docs/firebase_setup.md)

### "Microphone not working"

- Ensure browser has microphone permissions
- Voice input requires HTTPS (or localhost)
- Check browser console for WebRTC errors
- Try different browser (Chrome/Edge recommended)

### "Voice transcription inaccurate"

- Speak clearly and at moderate pace
- Reduce background noise
- Check microphone quality
- Set correct language in `VOICE_CONFIG`

### "Audio doesn't play"

- Browser autoplay policies may block audio
- Interact with page first (click anywhere)
- Check browser audio settings
- Ensure speakers/headphones connected

## 🎓 Learning Resources

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API Guide](https://platform.openai.com/docs/introduction)
- [OpenAI Whisper](https://platform.openai.com/docs/guides/speech-to-text)
- [OpenAI TTS](https://platform.openai.com/docs/guides/text-to-speech)
- [Firebase Firestore Guide](https://firebase.google.com/docs/firestore)
- [RAG Explained](https://python.langchain.com/docs/use_cases/question_answering/)

## 🚀 Roadmap

Completed features:

- [x] Voice input/output with OpenAI Whisper & TTS
- [x] Conversational context awareness
- [x] Cloud storage with Firebase
- [x] Multi-tool reasoning agent
- [x] Document Q&A with RAG

Potential future enhancements:

- [ ] User authentication
- [ ] Multiple LLM provider support (Anthropic Claude, Google Gemini)
- [ ] Multi-language UI
- [ ] Export conversations to PDF
- [ ] Custom tool marketplace
- [ ] Advanced analytics dashboard
- [ ] Voice command shortcuts ("clear chat", "new session")
- [ ] Streaming audio responses
- [ ] Custom voice profiles

---

## 📊 Project Stats

- **7 Built-in Tools** (Web search, Weather, Currency, Stocks, Calculator, Documents, Voice)
- **Voice I/O** (Speech recognition & natural TTS with 6 voices)
- **Conversational Context** (Understands pronouns and references)
- **Cloud Storage** (Firebase integration with session management)
- **Production Ready** (Modular architecture, error handling, comprehensive docs)

---

## 📚 Documentation

- **[README.md](README.md)** - Main documentation (you are here)
- **[firebase_setup.md](docs/firebase_setup.md)** - Cloud storage setup guide
- **[VOICE_MODULE_DOCUMENTATION.md](docs/VOICE_MODULE_DOCUMENTATION.md)** - Complete voice module technical guide
- **[.env.example](.env.example)** - Environment variables template

---

**Happy Coding! 🚀**

Built with ❤️ using LangChain, Streamlit, OpenAI, and Firebase

**New to voice features?** Check out [VOICE_MODULE_DOCUMENTATION.md](docs/VOICE_MODULE_DOCUMENTATION.md) for a complete technical guide!
