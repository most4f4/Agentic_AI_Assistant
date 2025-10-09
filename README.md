# 🤖 AI Assistant with RAG & Reasoning Agent

A powerful AI assistant built with LangChain and Streamlit that can reason about which tools to use, search the web, answer questions from uploaded documents, and perform various tasks autonomously.

## ✨ Features

- **🧠 Reasoning Agent**: Uses GPT-4 to intelligently decide which tools to use
- **📄 Document Q&A (RAG)**: Upload PDFs, Word docs, or text files and ask questions
- **🔍 Web Search**: Search for current information and news
- **🌤️ Weather**: Get real-time weather for any city
- **💱 Currency Converter**: Convert between major currencies
- **📊 Stock Prices**: Look up current stock information
- **🧮 Calculator**: Perform mathematical calculations

## 📁 Project Structure

```
ai_assistant/
│
├── app.py                      # Main entry point
├── requirements.txt            # Dependencies
├── .env                        # API keys (create from .env.example)
├── .env.example               # Example environment variables
├── README.md                   # This file
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
│   └── rag_chain.py           # RAG chain creation
│
├── ui/
│   ├── __init__.py
│   ├── sidebar.py             # Sidebar components
│   └── chat.py                # Chat interface
│
└── utils/
    ├── __init__.py
    └── helpers.py             # Helper functions
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

### Document Q&A

1. Click "📁 Upload Documents" in the sidebar
2. Upload your PDF, Word, or text files
3. Ask questions like:
   - "What is this document about?"
   - "Summarize the key points"
   - "What are the main conclusions?"

### Multi-Tool Queries

The agent can use multiple tools in one query:

```
"What's the weather in Paris and how much is 50 EUR in USD?"
```

## 🛠️ Configuration

Edit `config/settings.py` to customize:

- **LLM Model**: Change the GPT model
- **RAG Settings**: Adjust chunk size, overlap, retrieval count
- **Agent Behavior**: Modify verbosity, max iterations
- **Example Questions**: Add your own example prompts

## 📦 Adding New Tools

To add a new tool:

1. Create a new file in `tools/` (e.g., `tools/my_tool.py`)
2. Define your tool using the `@tool` decorator:

```python
from langchain.tools import tool

@tool
def my_tool(input: str) -> str:
    """Description of what your tool does"""
    # Your tool logic here
    return result
```

3. Import and add to `tools/__init__.py`
4. Add to the tools list in `agents/agent_setup.py`

## 🧪 Testing

Run individual modules:

```bash
# Test a specific tool
python -c "from tools.weather_tool import get_weather; print(get_weather('London'))"
```

## 📝 API Keys Required

| Service        | Purpose            | Get Key From                                     |
| -------------- | ------------------ | ------------------------------------------------ |
| OpenAI         | GPT-4 & Embeddings | [OpenAI Platform](https://platform.openai.com/)  |
| SerpAPI        | Web Search         | [SerpAPI](https://serpapi.com/)                  |
| OpenWeatherMap | Weather Data       | [OpenWeatherMap](https://openweathermap.org/api) |

## 🤝 Contributing

Feel free to:

- Add new tools
- Improve existing features
- Fix bugs
- Enhance documentation

## 📄 License

MIT License - feel free to use this project for learning or commercial purposes.

## 🙏 Acknowledgments

Built with:

- [LangChain](https://python.langchain.com/) - Agent framework
- [Streamlit](https://streamlit.io/) - Web interface
- [OpenAI](https://openai.com/) - Language models
- [ChromaDB](https://www.trychroma.com/) - Vector database

## 📧 Support

If you encounter issues:

1. Check that all API keys are correctly set in `.env`
2. Verify all dependencies are installed
3. Make sure you're using Python 3.8+

## 🎓 Learning Resources

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API Guide](https://platform.openai.com/docs/introduction)

---

**Happy Coding! 🚀**
