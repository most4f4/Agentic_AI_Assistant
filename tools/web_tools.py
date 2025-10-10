"""
Web search tool for finding current information
"""
import os
from langchain.tools import tool
from tavily import TavilyClient


@tool
def web_search(query: str) -> str:
    """Search the web for current information, news, facts, or any information you don't know. 
    Use this when the user asks about current events, latest news, prices, or specific facts."""
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "Tavily API key not configured. Please add TAVILY_API_KEY to your .env file"
        
        client = TavilyClient(api_key=api_key)
        
        # Search with Tavily
        results = client.search(
            query=query,
            max_results=5,  # Number of results
            include_answer=True,  # Get AI-generated answer
            include_raw_content=False,  # Don't need raw HTML
        )

        # Format results
        if results.get('answer'):
            # Tavily provides a direct answer
            answer = results['answer']
            sources = "\n\nSources:\n"
            for i, result in enumerate(results.get('results', [])[:3], 1):
                sources += f"{i}. {result['title']}: {result['url']}\n"
            
            return f"{answer}{sources}"
        else:
            # Fallback to result summaries
            formatted = "Search results:\n\n"
            for i, result in enumerate(results.get('results', [])[:5], 1):
                formatted += f"{i}. {result['title']}\n"
                formatted += f"   {result['content'][:200]}...\n"
                formatted += f"   Source: {result['url']}\n\n"
            
            return formatted
    except Exception as e:
        return f"Search failed: {e}"