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
        verbose=AGENT_CONFIG["verbose"],
        handle_parsing_errors=AGENT_CONFIG["handle_parsing_errors"],
        max_iterations=AGENT_CONFIG["max_iterations"],
    )
    
    return agent_executor