import os
from dotenv import load_dotenv
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "false"

from langchain.chat_models import init_chat_model
from langchain_community.utilities import SerpAPIWrapper

# Setup
groq_api_key = os.getenv("GROQ_API_KEY")
llm = init_chat_model(
    model="llama-3.1-8b-instant",
    model_provider="groq",
    api_key=groq_api_key
)

serpapi_key=os.getenv("SERPAPI_API_KEY")
search = SerpAPIWrapper(serpapi_api_key=serpapi_key)

class EnhancedAI:
    def __init__(self, llm, search):
        self.llm = llm
        self.search = search
    
    def search_and_answer(self, question):
        """Search web and get AI summary"""
        search_results = self.search.run(question)
        prompt = f"Question: {question}\nSearch results: {search_results}\nProvide a clear, concise answer:"
        response = self.llm.invoke(prompt)
        return response.content

    def weather(self, city):
        """Get weather for a city"""
        weather_data = self.search.run(f"weather in {city} today")
        prompt = f"Summarize the weather in {city} in one sentence: {weather_data}"
        response = self.llm.invoke(prompt)
        return response.content

    def news(self, topic):
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

    def calculate(self, expression):
        """Basic calculator"""
        try:
            result = eval(expression)
            return f"{expression} = {result}"
        except:
            return "Invalid math expression"

    def chat(self, message):
        """General conversation"""
        response = self.llm.invoke(message)
        return response.content

# Create enhanced assistant
ai = EnhancedAI(llm, search)

def main():
    print("Enhanced AI Assistant")
    print("Commands: weather <city>, news <topic>, stock <ticker>, calc <math>, or just ask anything")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        try:
            # Parse commands
            if user_input.startswith("weather "):
                city = user_input[8:]
                response = ai.weather(city)
            
            elif user_input.startswith("news "):
                topic = user_input[5:]
                response = ai.news(topic)
            
            elif user_input.startswith("stock "):
                ticker = user_input[6:]
                response = ai.stock_price(ticker)
            
            elif user_input.startswith("calc "):
                expression = user_input[5:]
                response = ai.calculate(expression)
            
            else:
                # For other questions, decide if search is needed
                search_keywords = ["latest", "current", "today", "news", "price", "what is", "who is"]
                needs_search = any(keyword in user_input.lower() for keyword in search_keywords)
                
                if needs_search:
                    response = ai.search_and_answer(user_input)
                else:
                    response = ai.chat(user_input)
            
            print(f"AI: {response}\n")
            
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()