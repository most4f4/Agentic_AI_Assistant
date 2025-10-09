from regex import search
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
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

class EnhancedAI:
    def __init__(self, llm, search):
        self.llm = llm
        self.search = search

    def search_and_answer(self, question):
        """Search and get AI response"""
        search_results = self.search.run(question)
        prompt = f"Question: {question}\nSearch results: {search_results}\nProvide a clear, helpful answer:"
        response = self.llm.invoke(prompt)
        return response.content
    
    def weather_forecast(self, city, days=1):
        """Extended weather forecast"""
        if days == 1:
            query = f"weather in {city} today"
        else:
            query = f"{days} day weather forecast {city}"
        weather_data = self.search.run(query)
        prompt = f"Provide a {days}-day weather forecast for {city}: {weather_data}"
        response = self.llm.invoke(prompt)
        return response.content
    
    def compare_topics(self, topic1, topic2):
        """Compare two topics"""
        data1 = self.search.run(f"information about {topic1}")
        data2 = self.search.run(f"information about {topic2}")
        prompt = f"Compare {topic1} vs {topic2}:\n{topic1}: {data1}\n{topic2}: {data2}\nProvide a detailed comparison:"
        response = self.llm.invoke(prompt)
        return response.content
    
    def explain_concept(self, concept, level="beginner"):
        """Explain complex concepts at different levels"""
        search_data = self.search.run(f"what is {concept} explained simply")
        if level == "beginner":
            prompt = f"Explain {concept} in simple terms for a beginner: {search_data}"
        elif level == "advanced":
            prompt = f"Explain {concept} in detail for an advanced learner: {search_data}"
        else:
            prompt = f"Explain {concept} at an intermediate level: {search_data}"
        response = self.llm.invoke(prompt)
        return response.content
    
    def research_topic(self, topic):
        """In-depth research on a topic"""
        searches = [
            f"{topic} overview",
            f"{topic} latest news 2024",
            f"{topic} pros and cons",
            f"{topic} future trends"
        ]
        all_data = []
        for search_query in searches:
            data = self.search.run(search_query)
            all_data.append(data)
        combined_data = "\n".join(all_data)
        prompt = f"Create a comprehensive research report on {topic}: {combined_data}"
        response = self.llm.invoke(prompt)
        return response.content
    
    def fact_check(self, statement):
        """Fact-check a statement"""
        search_data = self.search.run(f"fact check: {statement}")
        prompt = f"Fact-check this statement: '{statement}'\nEvidence: {search_data}\nIs this true or false? Explain why."
        response = self.llm.invoke(prompt)
        return response.content
    
    def calculator_tool(self, expression):
        """Mathematical calculations"""
        try:
            allowed_chars = set('0123456789+-*/.() ')
            if not set(expression).issubset(allowed_chars):
                return "Error: Only basic math operations allowed"
            result = eval(expression)
            return f"{expression} = {result}"
        except Exception as e:
            return f"Calculation error: {e}"
        
    def currency_converter(self, amount, from_currency, to_currency):
        """Currency conversion"""
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
            response = requests.get(url)
            data = response.json()
            if to_currency.upper() in data['rates']:
                rate = data['rates'][to_currency.upper()]
                converted = amount * rate
                return f"{amount} {from_currency.upper()} = {converted:.2f} {to_currency.upper()}"
            else:
                return f"Currency {to_currency} not found"
        except Exception as e:
            return f"Currency conversion failed: {e}"
        
    def news_summary(self, topic):
        """Get latest news on a topic"""
        news_data = self.search.run(f"latest news {topic}")
        prompt = f"Summarize the latest news about {topic}: {news_data}"
        response = self.llm.invoke(prompt)
        return response.content
    
    def stock_price(self, ticker):
        """Get stock price"""
        stock_data = self.search.run(f"{ticker} stock price today")
        prompt = f"What is {ticker} stock price? Data: {stock_data}"
        response = self.llm.invoke(prompt)
        return response.content
    
    def direct_chat(self, message):
        """General conversation"""
        response = self.llm.invoke(message)
        return response.content


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
    return EnhancedAI(llm, search)

def save_conversation_history():
    """Save conversation to file"""
    if st.session_state.messages:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(st.session_state.messages, f, indent=2)
        return filename
    return None


# Main app
def main():
    st.title("🤖 Enhanced AI Assistant")
    st.markdown("Choose a feature and interact with AI!")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Setup AI
    ai = setup_ai()
    
    # Sidebar with feature selection
    st.sidebar.title("Select Feature")
    
    feature = st.sidebar.radio(
        "Choose what you want to do:",
        [
            "💬 General Chat",
            "🌤️ Weather Forecast", 
            "📰 Latest News",
            "📊 Stock Prices",
            "🧮 Calculator",
            "💱 Currency Converter",
            "🔍 Web Search",
            "⚖️ Compare Topics",
            "📚 Explain Concept",
            "🔬 Research Topic",
            "✅ Fact Check"
        ]
    )
    
    st.sidebar.markdown("---")
    
    # Chat controls
    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.sidebar.markdown(f"**Messages:** {len(st.session_state.messages)}")
    
    # Main content area based on selected feature
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("Input")
        
        # Different inputs based on selected feature
        if feature == "💬 General Chat":
            user_input = st.text_area("Ask me anything:", height=100)
            
        elif feature == "🌤️ Weather Forecast":
            city = st.text_input("Enter city name:")
            days = st.slider("Number of days:", 1, 7, 1)
            user_input = f"{city} for {days} days" if city else ""
            
        elif feature == "📰 Latest News":
            topic = st.text_input("Enter topic for news:")
            user_input = topic
            
        elif feature == "📊 Stock Prices":
            ticker = st.text_input("Enter stock ticker (e.g., AAPL, GOOGL):")
            user_input = ticker
            
        elif feature == "🧮 Calculator":
            expression = st.text_input("Enter math expression (e.g., 25*8+10):")
            user_input = expression
            
        elif feature == "💱 Currency Converter":
            col_a, col_b = st.columns(2)
            with col_a:
                amount = st.number_input("Amount:", min_value=0.01, value=100.0)
                from_curr = st.selectbox("From:", ["USD", "EUR", "GBP", "JPY", "CAD"])
            with col_b:
                to_curr = st.selectbox("To:", ["EUR", "USD", "GBP", "JPY", "CAD"])
            user_input = f"{amount} {from_curr} to {to_curr}"
            
        elif feature == "🔍 Web Search":
            query = st.text_input("Enter search query:")
            user_input = query
            
        elif feature == "⚖️ Compare Topics":
            topic1 = st.text_input("First topic:")
            topic2 = st.text_input("Second topic:")
            user_input = f"{topic1} vs {topic2}" if topic1 and topic2 else ""
            
        elif feature == "📚 Explain Concept":
            concept = st.text_input("Enter concept to explain:")
            level = st.selectbox("Explanation level:", ["beginner", "intermediate", "advanced"])
            user_input = f"{concept} at {level} level" if concept else ""
            
        elif feature == "🔬 Research Topic":
            topic = st.text_input("Enter topic to research:")
            user_input = topic
            
        elif feature == "✅ Fact Check":
            statement = st.text_area("Enter statement to fact-check:", height=100)
            user_input = statement
        
        # Submit button
        submit_button = st.button("Submit", type="primary", disabled=not user_input)
    
    with col2:
        st.subheader("Response")
        
        # Process input when submitted
        if submit_button and user_input:
            with st.spinner("Processing..."):
                try:
                    # Process based on selected feature
                    if feature == "💬 General Chat":
                        response = ai.direct_chat(user_input)
                    elif feature == "🌤️ Weather Forecast":
                        response = ai.weather_forecast(city, days)
                    elif feature == "📰 Latest News":
                        response = ai.news_summary(user_input)
                    elif feature == "📊 Stock Prices":
                        response = ai.stock_price(user_input)
                    elif feature == "🧮 Calculator":
                        response = ai.calculator_tool(user_input)
                    elif feature == "💱 Currency Converter":
                        response = ai.currency_converter(amount, from_curr, to_curr)
                    elif feature == "🔍 Web Search":
                        response = ai.search_and_answer(user_input)
                    elif feature == "⚖️ Compare Topics":
                        response = ai.compare_topics(topic1, topic2)
                    elif feature == "📚 Explain Concept":
                        response = ai.explain_concept(concept, level)
                    elif feature == "🔬 Research Topic":
                        response = ai.research_topic(user_input)
                    elif feature == "✅ Fact Check":
                        response = ai.fact_check(user_input)
                    
                    # Display response
                    st.markdown("### AI Response:")
                    st.markdown(response)
                    
                    # Add to chat history
                    st.session_state.messages.append({
                        "feature": feature,
                        "input": user_input,
                        "response": response,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # Show recent chat history
        if st.session_state.messages:
            st.markdown("---")
            st.markdown("### Recent History:")
            for msg in st.session_state.messages[-3:]:  # Show last 3 interactions
                with st.expander(f"{msg['feature']} - {msg['timestamp']}"):
                    st.write(f"**Input:** {msg['input']}")
                    st.write(f"**Response:** {msg['response'][:200]}...")

if __name__ == "__main__":
    main()