"""
Stock price lookup tool
"""
import os
from langchain.tools import tool
from langchain.pydantic_v1 import BaseModel, Field
from langchain_community.utilities import SerpAPIWrapper


class StockInput(BaseModel):
    ticker: str = Field(description="The stock ticker symbol (e.g., AAPL, GOOGL, TSLA)")


@tool(args_schema=StockInput)
def get_stock_price(ticker: str) -> str:
    """Get current stock price and information for a given stock ticker symbol.
    Works with major stock exchanges like NYSE, NASDAQ, etc."""
    try:
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        search = SerpAPIWrapper(serpapi_api_key=serpapi_key)
        stock_data = search.run(f"{ticker} stock price today current")
        return f"Stock information for {ticker.upper()}:\n{stock_data}"
    except Exception as e:
        return f"Stock price lookup failed: {e}"