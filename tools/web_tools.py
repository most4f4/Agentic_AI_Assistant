"""
Web search tool for finding current information
"""
import os
from langchain.tools import tool
from langchain_community.utilities import SerpAPIWrapper


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