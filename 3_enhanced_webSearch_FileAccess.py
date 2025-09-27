import os
# we need json to save conversation history
import json
from datetime import datetime
# we need load_dotenv() to load the environment variables from the .env file
from dotenv import load_dotenv
load_dotenv()

# Disable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from langchain.chat_models import init_chat_model
from langchain_community.utilities import SerpAPIWrapper

#---------------------
# Setup LLM 
#---------------------
groq_api_key = os.getenv("GROQ_API_KEY")
llm = init_chat_model(
    model="llama-3.1-8b-instant",
    model_provider="groq",
    api_key=groq_api_key
)

#---------------------
# Setup web search tool
#---------------------
serpapi_key=os.getenv("SERPAPI_API_KEY")
search = SerpAPIWrapper(serpapi_api_key=serpapi_key)

#---------------------
# Enhanced AI class with more features
#---------------------
class EnhancedAI:
    def __init__(self, llm, search):
        self.llm = llm
        self.search = search
        self.conversation_history = []
        self.user_preferences = {}

    def log_conversation(self, user_input, ai_response):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "user": user_input,
            "ai": ai_response
        }
        self.conversation_history.append(entry)
        
        # Save to file
        with open("conversation_history.json", "w") as f:
            json.dump(self.conversation_history, f, indent=4)

    def search_with_context(self, question):
        """Search with conversation context"""
        # Add recent context to search
        context = ""
        if len(self.conversation_history) > 0:
            recent = self.conversation_history[-2]
            context = f"Recent context: {recent}. "

        search_results = self.search.run(context + " " + question)
        prompt = f"{context}Question: {question}\nSearch results: {search_results}\nProvide a detailed answer:"
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
            f"{topic} future trends",
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
    
    def translate_and_explain(self, text, target_language):
        """Translate text and explain cultural context"""
        search_data = self.search.run(f"translate '{text}' to {target_language}")
        prompt = f"Translate '{text}' to {target_language} and explain any cultural context: {search_data}"
        response = self.llm.invoke(prompt)
        return response.content
    
    def recipe_finder(self, ingredients):
        """Find recipes with available ingredients"""
        search_data = self.search.run(f"recipes with {ingredients}")
        prompt = f"Suggest recipes I can make with these ingredients: {ingredients}\nData: {search_data}"
        response = self.llm.invoke(prompt)
        return response.content
    
    def analyze_sentiment(self, text):
        """Analyze sentiment and provide insights"""
        prompt = f"Analyze the sentiment of this text and provide insights: '{text}'"
        response = self.llm.invoke(prompt)
        return response.content

#---------------------
# Create enhanced assistant
#---------------------
ai = EnhancedAI(llm, search)

#---------------------
# Main interaction loop
#---------------------
def main():
    print("Advanced AI Assistant")
    print("Commands:")
    print("- weather <city> [days]")
    print("- compare <topic1> vs <topic2>")
    print("- explain <concept> [level: beginner/intermediate/advanced]")
    print("- research <topic>")
    print("- fact-check <statement>")
    print("- translate <text> to <language>")
    print("- recipe <ingredients>")
    print("- sentiment <text>")
    print("- Or just ask anything!")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        try:
            response = ""

            # Parse commands
            if user_input.startswith("weather "):
                parts = user_input[8:].split()
                city = parts[0] # [0] means first element of the list separated by space
                days = int(parts[1]) if len(parts) > 1 else 1
                response = ai.weather_forecast(city, days)
            
            elif " vs " in user_input and user_input.startswith("compare "):
                topics = user_input[8:].split(" vs ")
                response = ai.compare_topics(topics[0].strip(), topics[1].strip())
            
            elif user_input.startswith("explain "):
                parts = user_input[8:].split(" level:")
                concept = parts[0].strip()
                level = parts[1].strip() if len(parts) > 1 else "beginner"
                response = ai.explain_concept(concept, level)
            
            elif user_input.startswith("research "):
                topic = user_input[9:]
                response = ai.research_topic(topic)

            elif user_input.startswith("fact-check "):
                statement = user_input[11:]
                response = ai.fact_check(statement)
            
            elif " to " in user_input and user_input.startswith("translate "):
                parts = user_input[10:].split(" to ")
                text = parts[0].strip()
                language = parts[1].strip()
                response = ai.translate_and_explain(text, language)
            
            elif user_input.startswith("recipe "):
                ingredients = user_input[7:]
                response = ai.recipe_finder(ingredients)
            
            elif user_input.startswith("sentiment "):
                text = user_input[10:]
                response = ai.analyze_sentiment(text)
            
            else:
                response = ai.search_with_context(user_input)
            
            print(f"AI: {response}\n")
            ai.log_conversation(user_input, response)
            
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()