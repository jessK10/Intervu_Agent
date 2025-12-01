"""
Google ADK Package (Compatibility Layer)

This package provides Google ADK compatibility using google-generativeai.

Usage:
    from app.google_adk import LLMAgent
    from app.google_adk.llms import GeminiModel
    from app.google_adk.tools import Tool
"""

import google.generativeai as genai
from typing import Dict, Any, Optional, List
import json
import asyncio

# Import from llms and tools modules
from .llms import GeminiModel
from .tools import Tool

# Define core agent classes directly here

class Agent:
    """Base ADK-compatible Agent class."""
    def __init__(self, name: str):
        self.name = name
    
    async def run(self, input_data: Any) -> Any:
        raise NotImplementedError("Subclasses must implement run()")


class LLMAgent(Agent):
    """ADK-compatible LLMAgent that uses Gemini under the hood."""
    
    def __init__(
        self,
        name: str,
        model: GeminiModel,
        instructions: str,
        tools: Optional[List] = None
    ):
        super().__init__(name)
        self.model = model
        self.instructions = instructions
        self.tools = tools or []
    
    async def run(self, input_data: Any) -> str:
        if isinstance(input_data, dict):
            input_str = json.dumps(input_data)
        else:
            input_str = str(input_data)
        
        prompt = f"""{self.instructions}

User Input:
{input_str}
"""
        response = await self.model.generate(prompt)
        return response


class SequentialAgent(Agent):
    """ADK-compatible Sequential agent."""
    
    def __init__(self, name: str, agents: List[Agent]):
        super().__init__(name)
        self.agents = agents
    
    async def run(self, input_data: Any) -> Any:
        result = input_data
        for agent in self.agents:
            result = await agent.run(result)
        return result


class ParallelAgent(Agent):
    """ADK-compatible Parallel agent."""
    
    def __init__(self, name: str, agents: List[Agent]):
        super().__init__(name)
        self.agents = agents
    
    async def run(self, input_data: Any) -> List[Any]:
        tasks = [agent.run(input_data) for agent in self.agents]
        results = await asyncio.gather(*tasks)
        return list(results)


class LoopAgent(Agent):
    """ADK-compatible Loop agent."""
    
    def __init__(self, name: str, agent: Agent, max_iterations: int = 5):
        super().__init__(name)
        self.agent = agent
        self.max_iterations = max_iterations
    
    async def run(self, input_data: Any) -> Any:
        result = input_data
        for i in range(self.max_iterations):
            result = await self.agent.run(result)
        return result


# Create sub-modules for compatibility
from . import llms
from . import tools

__all__ = [
    "Agent",
    "LLMAgent",
    "SequentialAgent", 
    "ParallelAgent",
    "LoopAgent",
    "llms",
    "tools"
]

__version__ = "0.1.0-compat"
