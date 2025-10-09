"""
Calculator tool for mathematical operations
"""
from langchain.tools import tool
from langchain.pydantic_v1 import BaseModel, Field


class CalculatorInput(BaseModel):
    expression: str = Field(description="A mathematical expression to calculate (e.g., '25*8+10' or '(100-25)/3')")


@tool(args_schema=CalculatorInput)
def calculator(expression: str) -> str:
    """Perform mathematical calculations. Supports basic operations: +, -, *, /, and parentheses.
    Use this for any math problems or calculations."""
    try:
        # Security: only allow safe mathematical characters
        allowed_chars = set('0123456789+-*/.() ')
        if not set(expression).issubset(allowed_chars):
            return "Error: Only basic math operations allowed (+, -, *, /, parentheses)"
        
        result = eval(expression)
        return f"Calculation: {expression} = {result}"
    except Exception as e:
        return f"Calculation error: {e}"