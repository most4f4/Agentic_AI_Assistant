import streamlit as st
import os
import requests
import tempfile

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Page configuration
st.set_page_config(
    page_title="AI Assistant M3",
    page_icon="🤖",
    layout="wide"
)

# ==================== TOOL DEFINITIONS ====================
@tool
def web_search(query: str) -> str:
    """Search the web for current information, news, facts, or any information you don't know. 
    Use this when the user asks about current events, latest news, prices, or specific facts."""
    try:
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        search = SerpAPIWrapper(serpapi_api_key=serpapi_key)
        results = search.run(query)
        return f"Search results: {results}"
    except Exception as e:
        return f"Search failed: {e}"

class WeatherInput(BaseModel):
    city: str = Field(description="The name of the city to get weather for")

@tool(args_schema=WeatherInput)
def get_weather(city: str) -> str:
    """Get current weather information for any city in the world.
    Returns temperature, conditions, humidity, and wind speed."""
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return "OpenWeatherMap API key not configured. Please add OPENWEATHER_API_KEY to your .env file"
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            weather_desc = data['weather'][0]['description'].title()
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            
            return f"Weather in {city}:\n- Temperature: {temp}°C (feels like {feels_like}°C)\n- Condition: {weather_desc}\n- Humidity: {humidity}%\n- Wind Speed: {wind_speed} m/s"
        else:
            return f"Could not find weather data for {city}. Please check the city name."
    except Exception as e:
        return f"Failed to get weather data: {e}"
    

class CurrencyInput(BaseModel):
    amount: float = Field(description="The amount of money to convert")
    from_currency: str = Field(description="The source currency code (e.g., USD, EUR, GBP)")
    to_currency: str = Field(description="The target currency code (e.g., USD, EUR, GBP)")

@tool(args_schema=CurrencyInput)
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert money from one currency to another. 
    Supports major currencies like USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY."""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
        response = requests.get(url)
        data = response.json()
        
        if to_currency.upper() in data['rates']:
            rate = data['rates'][to_currency.upper()]
            converted = amount * rate
            return f"{amount} {from_currency.upper()} = {converted:.2f} {to_currency.upper()}\nExchange Rate: 1 {from_currency.upper()} = {rate:.4f} {to_currency.upper()}"
        else:
            return f"Currency {to_currency} not found. Please use valid currency codes."
    except Exception as e:
        return f"Currency conversion failed: {e}"
    
class StockInput(BaseModel):
    ticker: str = Field(description="The stock ticker symbol (e.g., AAPL, GOOGL, TSLA)")


@tool(args_schema=StockInput)
def get_stock_price(ticker: str) -> str:
    """Get current stock price and information for a given stock ticker symbol.
    Works with major stock exchanges like NYSE, NASDAQ, etc."""
    try:
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        search = SerpAPIWrapper(serpapi_api_key=serpapi_key)
        stock_data = search.run(f"{ticker} stock price today current")
        return f"Stock information for {ticker.upper()}:\n{stock_data}"
    except Exception as e:
        return f"Stock price lookup failed: {e}"


class CalculatorInput(BaseModel):
    expression: str = Field(description="A mathematical expression to calculate (e.g., '25*8+10' or '(100-25)/3')")


@tool(args_schema=CalculatorInput)
def calculator(expression: str) -> str:
    """Perform mathematical calculations. Supports basic operations: +, -, *, /, and parentheses.
    Use this for any math problems or calculations."""
    try:
        # Security: only allow safe mathematical characters
        allowed_chars = set('0123456789+-*/.() ')
        if not set(expression).issubset(allowed_chars):
            return "Error: Only basic math operations allowed (+, -, *, /, parentheses)"
        
        result = eval(expression)
        return f"Calculation: {expression} = {result}"
    except Exception as e:
        return f"Calculation error: {e}"
    
class DocumentQueryInput(BaseModel):
    query: str = Field(description="The question to ask about the uploaded documents")

@tool(args_schema=DocumentQueryInput)
def query_documents(query: str) -> str:
    """Search and answer questions from uploaded documents. 
    Use this tool when the user asks questions about their uploaded files or documents.
    This tool has access to the content of any PDFs, Word docs, or text files the user has uploaded."""
    try:
        # Check if RAG system is available
        if "rag_chain" not in st.session_state or st.session_state.rag_chain is None:
            return "No documents have been uploaded yet. Please upload a document first using the sidebar."
        
        # Query the RAG system
        result = st.session_state.rag_chain.invoke({"input": query})
        return result["answer"]
    except Exception as e:
        return f"Error querying documents: {e}"
    
# ==================== RAG FUNCTIONS ====================

def load_document(file_path, file_type):
    """Load a document based on its type"""
    try:
        if file_type == "pdf":
            loader = PyPDFLoader(file_path)
        elif file_type == "txt":
            loader = TextLoader(file_path)
        elif file_type in ["docx", "doc"]:
            loader = UnstructuredWordDocumentLoader(file_path)
        else:
            return None
        
        documents = loader.load()
        return documents
    except Exception as e:
        st.error(f"Error loading document: {e}")
        return None


def process_documents(uploaded_files):
    """Process uploaded files and create a RAG chain"""
    all_documents = []
    
    # Process each uploaded file
    for uploaded_file in uploaded_files:
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Determine file type
        file_extension = uploaded_file.name.split(".")[-1].lower()
        
        # Load document
        documents = load_document(tmp_file_path, file_extension)
        
        if documents:
            all_documents.extend(documents)
        
        # Clean up temp file
        os.unlink(tmp_file_path)
    
    if not all_documents:
        return None
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(all_documents)
    
    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        collection_name="uploaded_docs"
    )
    
    # Create retriever
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )
    
    # Create QA chain
    llm = ChatOpenAI(
        model="gpt-4o",
    )
    
    qa_system_prompt = (
        "You are an assistant for question-answering tasks. Use "
        "the following pieces of retrieved context to answer the "
        "question. If you don't know the answer, just say that you "
        "don't know. Keep the answer concise and accurate."
        "\n\n"
        "{context}"
    )
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return rag_chain


# ==================== AGENT SETUP ====================
@st.cache_resource
def setup_agent():
    """Initialize the agent with all tools"""
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4o",
    )
    
    # Define all available tools
    tools = [
        web_search,
        get_weather,
        convert_currency,
        get_stock_price,
        calculator,
        query_documents,
    ]
    
    # Pull the prompt template from LangChain hub
    prompt = hub.pull("hwchase17/openai-tools-agent")
    
    # Create the agent
    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )
    
    # Create the agent executor
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
    )
    
    return agent_executor

# ==================== MAIN APP ====================
def main():
    st.title("🤖 AI Assistant with Reasoning Agent")
    st.markdown("Ask me anything! I can search the web, check weather, convert currency, look up stocks, and calculate.")


    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "rag_chain" not in st.session_state:
        st.session_state.rag_chain = None
    if "uploaded_files_names" not in st.session_state:
        st.session_state.uploaded_files_names = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None

    # Setup agent
    agent_executor = setup_agent()

    # Sidebar
    st.sidebar.title("🛠️ Agent Tools")
    st.sidebar.markdown("""
    The AI agent has access to these tools and will automatically choose which ones to use:
    
    **Available Tools:**
    - 🔍 **Web Search** - Search for current information
    - 🌤️ **Weather** - Get weather for any city
    - 💱 **Currency Converter** - Convert between currencies
    - 📊 **Stock Prices** - Look up stock information
    - 🧮 **Calculator** - Perform calculations
    - 📄 **Document Q&A** - Answer questions from uploaded files
    
    The agent will reason about your question and decide which tools to use!
    """)

    st.sidebar.markdown("---")

    # Document Upload Section
    st.sidebar.subheader("📁 Upload Documents")
    st.sidebar.markdown("Upload PDF, Word, or text files to ask questions about them!")
    
    uploaded_files = st.sidebar.file_uploader(
        "Choose files",
        type=["pdf", "txt", "docx", "doc"],
        accept_multiple_files=True,
        key="file_uploader"
    )
    
    if uploaded_files:
        current_files = [f.name for f in uploaded_files]
        
        # Check if files have changed
        if current_files != st.session_state.uploaded_files_names:
            with st.sidebar:
                with st.spinner("Processing documents..."):
                    rag_chain = process_documents(uploaded_files)
                    if rag_chain:
                        st.session_state.rag_chain = rag_chain
                        st.session_state.uploaded_files_names = current_files
                        st.success(f"✅ Processed {len(uploaded_files)} document(s)!")
                    else:
                        st.error("Failed to process documents")
        
        # Show uploaded files
        st.sidebar.markdown("**Uploaded Files:**")
        for file in uploaded_files:
            st.sidebar.text(f"📄 {file.name}")
    else:
        st.session_state.rag_chain = None
        st.session_state.uploaded_files_names = []
    
    st.sidebar.markdown("---")

    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    # Example questions
    st.sidebar.markdown("---")
    st.sidebar.markdown("**💡 Try asking:**")
    examples = [
        "What's the weather in Tokyo?",
        "Convert 100 USD to EUR",
        "What's the current price of AAPL stock?",
        "Calculate 245 * 67 + 891",
        "Search for the latest AI news",
        "What is this document about?",
        "Summarize the key points from my uploaded file"
    ]

    for example in examples:
        if st.sidebar.button(example, key=f"ex_{example}", use_container_width=True):
            # Add to chat
            # Store the question to process
            st.session_state.pending_question = example
            st.rerun()

    # Main chat interface
    st.markdown("---")
    st.subheader("💬 Chat")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Process pending question from sidebar button
    if st.session_state.pending_question:
        prompt = st.session_state.pending_question
        st.session_state.pending_question = None  # Clear it
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response using agent
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking and using tools..."):
                try:
                    # Invoke the agent
                    response = agent_executor.invoke({"input": prompt})
                    answer = response["output"]
                    
                    st.markdown(answer)
                    
                    # Add assistant response to chat
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    error_msg = f"I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        st.rerun()  # Rerun to show the complete exchange

    # User input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response using agent
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking and using tools..."):
                try:
                    # Invoke the agent
                    response = agent_executor.invoke({"input": prompt})
                    answer = response["output"]
                    
                    st.markdown(answer)
                    
                    # Add assistant response to chat
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    error_msg = f"I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Chat statistics at bottom
    if st.session_state.messages:
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        total_messages = len(st.session_state.messages)
        user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
        ai_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        docs_uploaded = len(st.session_state.uploaded_files_names)
        
        with col1:
            st.metric("Total Messages", total_messages)
        with col2:
            st.metric("Your Messages", user_messages)
        with col3:
            st.metric("AI Responses", ai_messages)
        with col4:
            st.metric("📄 Documents", docs_uploaded)


if __name__ == "__main__":
    main()





