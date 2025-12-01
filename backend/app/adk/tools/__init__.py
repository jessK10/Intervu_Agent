"""
MCP (Model Context Protocol) Tools Package

Custom and built-in tools for InterVu agents using Google ADK's
tool framework and MCP client integration.
"""

from google.adk.tools import Tool, SearchTool, CodeExecutionTool
from .cv_parser_tool import cv_parser_tool
from .job_scraper_tool import job_scraper_tool

# Built-in tools
search_tool = SearchTool()
code_exec_tool = CodeExecutionTool()

# Export all tools
__all__ = [
    "cv_parser_tool",
    "job_scraper_tool",
    "search_tool",
    "code_exec_tool"
]
