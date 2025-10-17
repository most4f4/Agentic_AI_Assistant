"""
Agent setup and initialization
"""
import streamlit as st
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI

from config.settings import LLM_CONFIG, AGENT_CONFIG
from tools import (
    web_search,
    get_weather,
    convert_currency,
    get_stock_price,
    calculator,
    query_documents
)


@st.cache_resource
def setup_agent():
    """Initialize the agent with all tools"""
    
    # Initialize LLM
    llm = ChatOpenAI(**LLM_CONFIG)
    
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
    # base_prompt = hub.pull("hwchase17/openai-tools-agent")

    # Enhance the system message to be more aware of uploaded documents
    enhanced_system_message = """You are a helpful AI assistant with access to various tools.

IMPORTANT INSTRUCTIONS FOR CONVERSATIONAL CONTEXT:
- Pay attention to the chat history to understand pronouns and references like "it", "that", "there", "this"
- When users ask follow-up questions, infer what they're referring to from the conversation history
- Examples:
  * If they asked about their job and then say "summarize it" → they mean their job
  * If they asked about a document and say "what else is in there" → they mean the document
  * If they asked about weather in Paris and say "convert 50 EUR to USD" → context is Paris

IMPORTANT INSTRUCTIONS FOR DOCUMENT QUERIES:
- When users ask about "my resume", "my job", "my experience", "my education", "my skills" or reference uploaded documents, you MUST use the query_documents tool first
- Do NOT say you don't have access to personal information without checking uploaded documents first
- Users may have uploaded their resume, CV, reports, or other documents - always check these before saying you can't help
- If a user mentions they uploaded something, believe them and use the query_documents tool
- Follow-up questions about documents (like "summarize it", "tell me more", "what else") should also use query_documents

Available tools and when to use them:
- query_documents: For ANY questions about uploaded files, resumes, personal documents, AND follow-ups about them
- web_search: For current events, news, latest information not in documents
- get_weather: For weather information
- convert_currency: For currency conversion
- get_stock_price: For stock market data
- calculator: For mathematical calculations

Always use the most appropriate tool for the user's question, considering the conversation context."""

    # Update the system message in the prompt
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    prompt = ChatPromptTemplate.from_messages([
    ("system", enhanced_system_message),           # ← Instructions
    MessagesPlaceholder("chat_history", optional=True),  # ← Memory
    ("human", "{input}"),                          # ← User question
    MessagesPlaceholder("agent_scratchpad"),       # ← Agent's thinking
])
    
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
        verbose=AGENT_CONFIG["verbose"],
        handle_parsing_errors=AGENT_CONFIG["handle_parsing_errors"],
        max_iterations=AGENT_CONFIG["max_iterations"],
    )
    
    return agent_executor