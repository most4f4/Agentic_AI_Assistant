import streamlit as st
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SerpAPIWrapper

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Page configuration
st.set_page_config(
    page_title="AI Assistant M3",
    page_icon="🤖",
    layout="wide"
)

# Initialize components
@st.cache_resource
def setup_ai():
    groq_api_key = os.getenv("GROQ_API_KEY")
    llm = init_chat_model(
        model="llama-3.1-8b-instant",
        model_provider="groq",
        api_key=groq_api_key
    )
    serpapi_key = os.getenv("SERPAPI_API_KEY")
    search = SerpAPIWrapper(serpapi_api_key=serpapi_key)
    return llm, search

def search_and_answer(llm, search, question):
    """Search and get AI response"""
    try:
        search_results = search.run(question)
        prompt = f"Question: {question}\nSearch results: {search_results}\nProvide a clear, helpful answer:"
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {e}"

def direct_chat(llm, message):
    """Direct chat without search"""
    try:
        response = llm.invoke(message)
        return response.content
    except Exception as e:
        return f"Error: {e}"

def get_weather_api(city):
    """Get weather from OpenWeatherMap API"""
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return "OpenWeatherMap API key not configured. Add OPENWEATHER_API_KEY to your .env file"
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            weather_desc = data['weather'][0]['description'].title()
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            
            return f"Weather in {city}:\nTemperature: {temp}°C (feels like {feels_like}°C)\nCondition: {weather_desc}\nHumidity: {humidity}%\nWind Speed: {wind_speed} m/s"
        else:
            return f"Weather data not found for {city}. Please check the city name."
    except Exception as e:
        return f"Weather API error: {e}"

def currency_converter(amount, from_curr, to_curr):
    """Convert currency using API"""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_curr.upper()}"
        response = requests.get(url)
        data = response.json()
        
        if to_curr.upper() in data['rates']:
            rate = data['rates'][to_curr.upper()]
            converted = amount * rate
            return f"{amount} {from_curr.upper()} = {converted:.2f} {to_curr.upper()}\nExchange Rate: 1 {from_curr.upper()} = {rate:.4f} {to_curr.upper()}"
        else:
            return f"Currency {to_curr} not found"
    except Exception as e:
        return f"Currency conversion failed: {e}"

def get_stock_price(ticker):
    """Get stock price (using web search as fallback)"""
    try:
        search = SerpAPIWrapper(serpapi_api_key=os.getenv("SERPAPI_API_KEY"))
        stock_data = search.run(f"{ticker} stock price today current")
        return f"Stock Price for {ticker.upper()}:\n{stock_data[:300]}..."
    except Exception as e:
        return f"Stock price lookup failed: {e}"

def calculate(expression):
    """Safe calculator"""
    try:
        allowed_chars = set('0123456789+-*/.() ')
        if not set(expression).issubset(allowed_chars):
            return "Error: Only basic math operations allowed (+, -, *, /, parentheses)"
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Calculation error: {e}"

# Main app
def main():
    st.title("🤖 AI Assistant M3")
    st.markdown("Chat with AI and use integrated tools in the sidebar!")

    st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        height: 60px;
        white-space: normal;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Setup AI components
    llm, search = setup_ai()

    # Sidebar
    st.sidebar.title("Settings")
    search_mode = st.sidebar.radio(
        "Chat Mode:",
        ["Auto (Smart)", "Always Search", "Chat Only"]
    )
    
    # Tool buttons in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Quick Tools:**")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        weather_btn = st.button("🌤️ Weather", use_container_width=True)
        stock_btn = st.button("📊 Stock", use_container_width=True)
    with col2:
        currency_btn = st.button("💱 Currency", use_container_width=True)
        calc_btn = st.button("🧮 Calculator", use_container_width=True)
    
    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.sidebar.markdown(f"**Messages:** {len(st.session_state.messages)}")

    # Modal-style containers using expanders
    # Weather Tool
    if weather_btn:
        st.session_state.show_weather = True
        
    if st.session_state.get('show_weather', False):
        with st.container():
            st.markdown("---")
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader("🌤️ Weather Tool")
            with col2:
                if st.button("✖️ Close", key="close_weather"):
                    st.session_state.show_weather = False
                    st.rerun()
            
            st.markdown("Get current weather information for any city")
            weather_city = st.text_input("Enter city name:", placeholder="e.g., London, Tokyo, New York", key="weather_input")
            
            if st.button("Get Weather", type="primary", key="get_weather_btn"):
                if weather_city:
                    with st.spinner("Fetching weather data..."):
                        weather_result = get_weather_api(weather_city)
                        st.success("Weather data retrieved!")
                        st.code(weather_result)
                else:
                    st.error("Please enter a city name")
            st.markdown("---")

    # Currency Converter
    if currency_btn:
        st.session_state.show_currency = True
        
    if st.session_state.get('show_currency', False):
        with st.container():
            st.markdown("---")
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader("💱 Currency Converter")
            with col2:
                if st.button("✖️ Close", key="close_currency"):
                    st.session_state.show_currency = False
                    st.rerun()
            
            st.markdown("Convert between different currencies")
            col1, col2, col3 = st.columns(3)
            with col1:
                amount = st.number_input("Amount:", min_value=0.01, value=100.0, key="curr_amount")
            with col2:
                from_curr = st.selectbox("From:", ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY"], key="from_curr")
            with col3:
                to_curr = st.selectbox("To:", ["EUR", "USD", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY"], key="to_curr")
            
            if st.button("Convert Currency", type="primary", key="convert_btn"):
                with st.spinner("Converting currency..."):
                    currency_result = currency_converter(amount, from_curr, to_curr)
                    st.success("Conversion completed!")
                    st.code(currency_result)
            st.markdown("---")

    # Stock Price Lookup
    if stock_btn:
        st.session_state.show_stock = True
        
    if st.session_state.get('show_stock', False):
        with st.container():
            st.markdown("---")
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader("📊 Stock Price Lookup")
            with col2:
                if st.button("✖️ Close", key="close_stock"):
                    st.session_state.show_stock = False
                    st.rerun()
            
            st.markdown("Get current stock price information")
            stock_ticker = st.text_input("Enter stock ticker:", placeholder="e.g., AAPL, GOOGL, TSLA", key="stock_input")
            
            if st.button("Get Stock Price", type="primary", key="stock_btn"):
                if stock_ticker:
                    with st.spinner("Fetching stock data..."):
                        stock_result = get_stock_price(stock_ticker)
                        st.success("Stock data retrieved!")
                        st.text_area("Stock Information:", value=stock_result, height=200, key="stock_result")
                else:
                    st.error("Please enter a stock ticker")
            st.markdown("---")

    # Calculator
    if calc_btn:
        st.session_state.show_calculator = True
        
    if st.session_state.get('show_calculator', False):
        with st.container():
            st.markdown("---")
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader("🧮 Calculator")
            with col2:
                if st.button("✖️ Close", key="close_calc"):
                    st.session_state.show_calculator = False
                    st.rerun()
            
            st.markdown("Perform mathematical calculations")
            calc_expression = st.text_input("Enter math expression:", placeholder="e.g., 25*8+10, (100-25)/3", key="calc_input")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Calculate", type="primary", key="calc_btn"):
                    if calc_expression:
                        with st.spinner("Calculating..."):
                            calc_result = calculate(calc_expression)
                            st.success("Calculation completed!")
                            st.code(calc_result)
                    else:
                        st.error("Please enter a mathematical expression")
            
            with col2:
                st.markdown("**Supported operations:**")
                st.markdown("- Addition: `+`")
                st.markdown("- Subtraction: `-`")  
                st.markdown("- Multiplication: `*`")
                st.markdown("- Division: `/`")
                st.markdown("- Parentheses: `()`")
            st.markdown("---")

    # Main Chat Interface
    st.subheader("💬 Chat")

    # Display chat history (like V1)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Decide whether to search based on mode and content
                if search_mode == "Always Search":
                    response = search_and_answer(llm, search, prompt)
                elif search_mode == "Chat Only":
                    response = direct_chat(llm, prompt)
                else:  # Auto mode
                    search_keywords = ["latest", "current", "today", "news", "price", "what is", "who is", "when did"]
                    needs_search = any(keyword in prompt.lower() for keyword in search_keywords)
                    if needs_search:
                        response = search_and_answer(llm, search, prompt)
                    else:
                        response = direct_chat(llm, prompt)

                st.markdown(response)

        # Add AI response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})

    # History Tab (below the chat)
    if st.session_state.messages:
        st.markdown("---")
        
        # Create tabs for history
        tab1, tab2 = st.tabs(["📜 Recent History", "📊 Chat Stats"])
        
        with tab1:
            st.markdown("**Last 10 messages:**")
            for i, msg in enumerate(st.session_state.messages[-10:], 1):
                role_icon = "👤" if msg["role"] == "user" else "🤖"
                with st.expander(f"{role_icon} {msg['role'].title()} - Message {len(st.session_state.messages)-10+i}"):
                    st.markdown(msg["content"])
        
        with tab2:
            total_messages = len(st.session_state.messages)
            user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
            ai_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Messages", total_messages)
            with col2:
                st.metric("User Messages", user_messages)
            with col3:
                st.metric("AI Messages", ai_messages)

if __name__ == "__main__":
    main()