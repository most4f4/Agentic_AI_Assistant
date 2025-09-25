# we need os to use os.getenv() to get the environment variables
import os

# we need load_dotenv() to load the environment variables from the .env file
from dotenv import load_dotenv
# run load_dotenv() to load the environment variables from the .env file
load_dotenv()

# Enable LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "false"  # Force to true
# os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
# os.environ["LANGSMITH_WORKSPACE_ID"] = "default"  # Add this line
# os.environ["LANGCHAIN_PROJECT"] = "my-ai-agent"
# os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

# Check if LangSmith is configured correctly
# langsmith_key = os.getenv("LANGSMITH_API_KEY")
# if not langsmith_key:
#     print("WARNING: LANGSMITH_API_KEY not found in .env file")
#     print("Get your key from: https://smith.langchain.com/")
# else:
#     print(f"LangSmith configured: {langsmith_key[:10]}...")



# init_chat_model is a function that initializes a chat model
from langchain.chat_models import init_chat_model
# SerpAPIWrapper is a tool that allows the agent to search the web
from langchain_community.utilities import SerpAPIWrapper
# initialize_agent is a function that initializes an agent
# Tool is a class that represents a tool
from langchain.agents import initialize_agent, Tool


# ---------------------
# Set up the LLM
# ---------------------
groq_api_key = os.getenv("GROQ_API_KEY")
llm = init_chat_model(
    model="llama-3.1-8b-instant",
    model_provider="groq",
    api_key=groq_api_key
)

# ---------------------
# Set up web search tool
# ---------------------
serpapi_key = os.getenv("SERPAPI_API_KEY")
search = SerpAPIWrapper(
    serpapi_api_key=serpapi_key
)

search_tool = Tool(
    name="Search",
    func=search.run,
    description="Use this tool to search the web for current information."
)

# ---------------------
# Create agent with search tool
# ---------------------

agent = initialize_agent(
    tools=[search_tool],
    llm=llm,
    agent="zero-shot-react-description", # "zero-shot-react-description" is a type of agent that uses the zero-shot-react-description strategy
    verbose=True,
    max_iterations=5,
    max_execution_time=30,
    handle_parsing_errors=True, # parse the errors means if the agent encounters an error, it will parse the error and return the error message
    early_stopping_method="generate"  # This helps it complete properly
)
# zero-shot-react-description strategy: 
# it’s a way to guide LLMs to think, do, and explain in one go, without requiring example demonstrations.

# ---------------------
# Run the agent and test it
# ---------------------

# Run search directly
weather_data = search.run("weather in Toronto today")

# Ask LLM to summarize
prompt = f"Based on this data: {weather_data}, summarize the weather in Toronto today in one concise sentence."
final_response = llm.invoke(prompt)
print("Weather in Toronto:", final_response.content)

    
