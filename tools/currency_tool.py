"""
Currency conversion tool
"""
import requests
from langchain.tools import tool
from langchain.pydantic_v1 import BaseModel, Field


class CurrencyInput(BaseModel):
    amount: float = Field(description="The amount of money to convert")
    from_currency: str = Field(description="The source currency code (e.g., USD, EUR, GBP)")
    to_currency: str = Field(description="The target currency code (e.g., USD, EUR, GBP)")


@tool(args_schema=CurrencyInput)
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert money from one currency to another. 
    Supports major currencies like USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY."""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
        response = requests.get(url)
        data = response.json()
        
        if to_currency.upper() in data['rates']:
            rate = data['rates'][to_currency.upper()]
            converted = amount * rate
            return f"{amount} {from_currency.upper()} = {converted:.2f} {to_currency.upper()}\nExchange Rate: 1 {from_currency.upper()} = {rate:.4f} {to_currency.upper()}"
        else:
            return f"Currency {to_currency} not found. Please use valid currency codes."
    except Exception as e:
        return f"Currency conversion failed: {e}"