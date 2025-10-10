# 🤖 AI Assistant with RAG & Reasoning Agent

A powerful AI assistant built with LangChain and Streamlit that can reason about which tools to use, search the web, answer questions from uploaded documents, and perform various tasks autonomously with full conversational context awareness.

## ✨ Features

- **🧠 Reasoning Agent**: Uses GPT-4 to intelligently decide which tools to use
- **💬 Conversational Context**: Understands follow-up questions and pronouns ("it", "that", "there")
- **📄 Document Q&A (RAG)**: Upload PDFs, Word docs, or text files and ask questions with conversation history
- **☁️ Cloud Storage (Optional)**: Save conversations to Firebase Firestore for persistence across sessions
- **🔍 Web Search**: Search for current information and news
- **🌤️ Weather**: Get real-time weather for any city
- **💱 Currency Converter**: Convert between major currencies
- **📊 Stock Prices**: Look up current stock information
- **🧮 Calculator**: Perform mathematical calculations

## 🆕 What's New

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

### **Cloud Storage (Optional)**

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
├── .env.example               # Example environment variables
├── README.md                   # This file
├── FIREBASE_SETUP.md          # Cloud storage setup guide
│
├── config/
│   ├── __init__.py
│   └── settings.py            # Configuration settings
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
│   └── chat.py                # Chat interface with context
│
└── utils/
    ├── __init__.py
    ├── helpers.py             # Helper functions
    └── firestore_manager.py   # Cloud storage manager
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

- **OpenAI API**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **SerpAPI**: Get from [SerpAPI](https://serpapi.com/)
- **OpenWeather**: Get from [OpenWeatherMap](https://openweathermap.org/api)

Optional (for cloud storage):

- **Firebase Firestore**: See [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for setup instructions

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

### Multi-Tool Queries

The agent can use multiple tools intelligently:

```
"What's the weather in Paris and how much is 50 EUR in USD?"
```

## ☁️ Cloud Storage (Optional)

### Enable Cloud Storage

1. Follow the setup guide: [FIREBASE_SETUP.md](FIREBASE_SETUP.md)
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

- Click "💾 Save to Cloud" to manually save
- Click "📥 Load from Cloud" to restore
- Enable "Auto-save messages" for automatic backup
- Switch between sessions in Session Management

## 🛠️ Configuration

Edit `config/settings.py` to customize:

### LLM Model

```python
LLM_CONFIG = {
    "model": "gpt-4o",  # Change model here
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

| Service        | Purpose            | Get Key From                                             | Required    |
| -------------- | ------------------ | -------------------------------------------------------- | ----------- |
| OpenAI         | GPT-4 & Embeddings | [OpenAI Platform](https://platform.openai.com/)          | ✅ Yes      |
| SerpAPI        | Web Search         | [SerpAPI](https://serpapi.com/)                          | ✅ Yes      |
| OpenWeatherMap | Weather Data       | [OpenWeatherMap](https://openweathermap.org/api)         | ✅ Yes      |
| Firebase       | Cloud Storage      | [Firebase Console](https://console.firebase.google.com/) | ⭕ Optional |

## 🎓 Key Concepts

### Conversational Agent

- Maintains chat history (last 10 messages)
- Understands pronouns and references
- Contextual tool selection

### Conversational RAG

- Document Q&A with memory
- Reformulates questions using history
- Separate RAG chat history (last 20 messages)

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

## 📄 License

MIT License - feel free to use this project for learning or commercial purposes.

## 🙏 Acknowledgments

Built with:

- [LangChain](https://python.langchain.com/) - Agent framework
- [Streamlit](https://streamlit.io/) - Web interface
- [OpenAI](https://openai.com/) - Language models
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Firebase Firestore](https://firebase.google.com/docs/firestore) - Cloud storage

## 📧 Support

If you encounter issues:

1. Check that all API keys are correctly set in `.env`
2. Verify all dependencies are installed (`pip install -r requirements.txt`)
3. Make sure you're using Python 3.8+
4. For cloud storage issues, see [FIREBASE_SETUP.md](FIREBASE_SETUP.md)

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
- See troubleshooting section in [FIREBASE_SETUP.md](FIREBASE_SETUP.md)

## 🎓 Learning Resources

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API Guide](https://platform.openai.com/docs/introduction)
- [Firebase Firestore Guide](https://firebase.google.com/docs/firestore)
- [RAG Explained](https://python.langchain.com/docs/use_cases/question_answering/)

## 🚀 Roadmap

Potential future enhancements:

- [ ] User authentication
- [ ] Multiple LLM provider support
- [ ] Voice input/output
- [ ] Export conversations to PDF
- [ ] Custom tool marketplace
- [ ] Advanced analytics dashboard

---

## 📊 Project Stats

- **6 Built-in Tools** (Web search, Weather, Currency, Stocks, Calculator, Documents)
- **Conversational Context** (Understands pronouns and references)
- **Cloud Storage** (Optional Firebase integration)
- **Production Ready** (Modular architecture, error handling)

---

**Happy Coding! 🚀**

Built with ❤️ using LangChain, Streamlit, and OpenAI
