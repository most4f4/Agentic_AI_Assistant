import os
# we need json to save conversation history
import json
import requests
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
# we need load_dotenv() to load the environment variables from the .env file
from dotenv import load_dotenv
load_dotenv()

# Disable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from langchain.chat_models import init_chat_model
from langchain_community.utilities import SerpAPIWrapper


class MultiToolAI:
    def __init__(self, llm):
        self.llm = llm

        # Tool 1: Web Search
        self.search = SerpAPIWrapper(serpapi_api_key=os.getenv("SERPAPI_API_KEY"))

        # Tool 2: Calculator (built-in)
        # Tool 3: File Operations (built-in)
        # Tool 4: Weather API (alternative to web search)
        # Tool 5: Email Sender 

    def web_search_tool(self, query):
        """Tool 1: Web search via SerpAPI"""
        try:
            results = self.search.run(query)
            return f"Search results: {results}"
        except Exception as e:
            return f"Search failed: {e}"
    
    def calculator_tool(self, expression):
        """Tool 2: Mathematical calculations"""
        try:
            # Safe evaluation - only allow math operations
            allowed_chars = set('0123456789+-*/.() ')
            if not set(expression).issubset(allowed_chars):
                return "Error: Only basic math operations allowed"
            result = eval(expression)
            return f"{expression} = {result}"
        except Exception as e:
            return f"Calculation error: {e}"
        
    def file_tool(self, operation, filename, content=None):
        """Tool 3: File operations"""
        try:
            if operation == "read":
                with open(filename, 'r') as f:
                    data = f.read()
                return f"File content: {data[:500]}..."
            
            elif operation == "write":
                with open(filename, 'w') as f:
                    f.write(content)
                return f"File '{filename}' written successfully"
            
            elif operation == "list":
                files = os.listdir('.')
                return f"Files in directory: {files}"
            
        except Exception as e:
            return f"File operation failed: {e}"
        
    def weather_api_tool(self, city):
        """Tool 4: Direct weather API (alternative to search)"""
        try:
            api_key = os.getenv("OPENWEATHER_API_KEY")
            if not api_key:
                return "OpenWeatherMap API key not configured"
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:
                weather_desc = data['weather'][0]['description']
                temp = data['main']['temp']
                humidity = data['main']['humidity']
                return f"Weather in {city}: {weather_desc}, Temp: {temp}°C, Humidity: {humidity}%"
        except Exception as e:
            return f"Weather API failed: {e}"
        
    def email_tool(self, to_email, subject, message):
        """Tool 5: Send email"""
        try:
            smtp_server = os.getenv("SMTP_SERVER")
            smtp_port = int(os.getenv("SMTP_PORT", 587))
            smtp_user = os.getenv("SMTP_USER")
            smtp_password = os.getenv("SMTP_PASSWORD")

            if not all([smtp_server, smtp_user, smtp_password]):
                return "SMTP configuration is incomplete"

            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = smtp_user
            msg['To'] = to_email

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, [to_email], msg.as_string())
            
            return f"Email sent to {to_email} successfully"
        except Exception as e:
            return f"Email sending failed: {e}"
        
        
    def currency_tool(self, amount, from_currency, to_currency):
        """Tool 6: Currency conversion"""
        try:
            # Using free currency API
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
        
    def decide_and_use_tool(self, user_input):
        """Decide which tool to use based on input"""
        user_lower = user_input.lower()
        
        # Math expressions
        if any(op in user_input for op in ['+', '-', '*', '/', '=', 'calculate']):
            # Extract the math expression
            for word in user_input.split():
                if any(op in word for op in ['+', '-', '*', '/']):
                    return self.calculator_tool(word)
            return self.calculator_tool(user_input)
        
        # File operations
        elif user_input.startswith("read file "):
            filename = user_input[10:]
            return self.file_tool("read", filename)
        
        elif user_input.startswith("save to "):
            parts = user_input.split(" content: ")
            filename = parts[0][8:]
            content = parts[1] if len(parts) > 1 else ""
            return self.file_tool("write", filename, content)
        
        # Currency conversion
        elif "convert" in user_lower and any(curr in user_lower for curr in ["usd", "eur", "gbp", "cad"]):
            # Simple parsing - you can make this more sophisticated
            words = user_input.split()
            try:
                amount = float(words[1])
                from_curr = words[2]
                to_curr = words[4]
                return self.currency_tool(amount, from_curr, to_curr)
            except:
                return "Format: convert 100 USD to EUR"
        
        
        # Weather (try API first, fallback to search)
        elif "weather" in user_lower:
            city = user_input.lower().replace("weather in ", "").replace("weather ", "")
            api_result = self.weather_api_tool(city)
            if "API key not configured" in api_result or "failed" in api_result:
                # Fallback to search
                search_result = self.web_search_tool(f"weather in {city}")
                prompt = f"Summarize weather: {search_result}"
                response = self.llm.invoke(prompt)
                return response.content
            return api_result
        
        # Default: use web search
        else:
            search_result = self.web_search_tool(user_input)
            prompt = f"Answer based on this data: {search_result}\nQuestion: {user_input}"
            response = self.llm.invoke(prompt)
            return response.content


#---------------------
# Setup LLM and tools
#---------------------
groq_api_key = os.getenv("GROQ_API_KEY")
llm = init_chat_model(
    model="llama-3.1-8b-instant",
    model_provider="groq",
    api_key=groq_api_key
)

ai = MultiToolAI(llm)


#---------------------
# Main interaction loop
#---------------------
def main():
    print("Multi-Tool AI Assistant")
    print("Available tools:")
    print("1. Web Search (default)")
    print("2. Calculator: '25 * 8' or 'calculate 100/4'")
    print("3. Files: 'read file notes.txt' or 'save to file.txt content: Hello'")
    print("4. Weather: 'weather in Tokyo'")
    print("5. Currency: 'convert 100 USD to EUR'")
    print("6. Email: 'send email to...' (needs setup)")
    print()
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            break
            
        try:
            response = ai.decide_and_use_tool(user_input)
            print(f"AI: {response}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()