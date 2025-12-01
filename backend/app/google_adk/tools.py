"""
Google ADK Tools - Compatibility Layer

Provides Tool decorator and built-in tools interface.
"""

from typing import Callable


class Tool:
    """
    ADK-compatible Tool decorator.
    
    Usage:
        @Tool(name="my_tool", description="Does something")
        async def my_tool(arg1: str) -> str:
            return f"Result: {arg1}"
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator that wraps the function."""
        func._is_tool = True
        func._tool_name = self.name
        func._tool_description = self.description
        return func


# Placeholder built-in tools
SearchTool = None
CodeExecutionTool = None

__all__ = ["Tool", "SearchTool", "CodeExecutionTool"]
