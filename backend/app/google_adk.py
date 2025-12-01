"""
Google ADK Compatibility Layer

Since google-adk is not yet publicly available, this module provides
a compatibility layer that implements Google ADK patterns using
google-generativeai as the underlying engine.

This allows you to write code using ADK syntax while still working.
"""

import google.generativeai as genai
from typing import Dict, Any, Optional, Callable, List
import json
import asyncio

__version__ = "0.1.0-compat"


class GeminiModel:
    """
    Wrapper for Gemini models compatible with ADK's model interface.
    """
    def __init__(self, model_name: str = "gemini-pro"):
        self.model_name = model_name
        self._model = genai.GenerativeModel(model_name)
    
    async def generate(self, prompt: str) -> str:
        """Generate content asynchronously."""
        response = await asyncio.to_thread(
            self._model.generate_content, prompt
        )
        return response.text
    
    def generate_sync(self, prompt: str) -> str:
        """Generate content synchronously."""
        response = self._model.generate_content(prompt)
        return response.text


class LLMAgent:
    """
    ADK-compatible LLMAgent that uses Gemini under the hood.
    
    Usage:
        agent = LLMAgent(
            name="my_agent",
            model=GeminiModel("gemini-pro"),
            instructions="You are a helpful assistant"
        )
        result = await agent.run("What is 2+2?")
    """
    
    def __init__(
        self,
        name: str,
        model: GeminiModel,
        instructions: str,
        tools: Optional[List] = None
    ):
        self.name = name
        self.model = model
        self.instructions = instructions
        self.tools = tools or []
    
    async def run(self, input_data: Any) -> str:
        """
        Execute the agent with given input.
        
        Args:
            input_data: Input string or dict
            
        Returns:
            Agent's response as string
        """
        # Convert input to string if needed
        if isinstance(input_data, dict):
            input_str = json.dumps(input_data)
        else:
            input_str = str(input_data)
        
        # Build prompt with instructions
        prompt = f"""{self.instructions}

User Input:
{input_str}
"""
        
        # Generate response
        response = await self.model.generate(prompt)
        return response


class Agent:
    """
    Base ADK-compatible Agent class.
    """
    
    def __init__(self, name: str):
        self.name = name
    
    async def run(self, input_data: Any) -> Any:
        """Override this method in subclasses."""
        raise NotImplementedError("Subclasses must implement run()")


class SequentialAgent(Agent):
    """
    ADK-compatible Sequential agent that runs agents in order.
    
    Usage:
        workflow = SequentialAgent(
            name="my_workflow",
            agents=[agent1, agent2, agent3]
        )
        result = await workflow.run(initial_input)
    """
    
    def __init__(self, name: str, agents: List[Agent]):
        super().__init__(name)
        self.agents = agents
    
    async def run(self, input_data: Any) -> Any:
        """Run agents sequentially, passing output to next."""
        result = input_data
        for agent in self.agents:
            result = await agent.run(result)
        return result


class ParallelAgent(Agent):
    """
    ADK-compatible Parallel agent that runs agents concurrently.
    
    Usage:
        workflow = ParallelAgent(
            name="parallel_workflow",
            agents=[agent1, agent2, agent3]
        )
        results = await workflow.run(input_data)
    """
    
    def __init__(self, name: str, agents: List[Agent]):
        super().__init__(name)
        self.agents = agents
    
    async def run(self, input_data: Any) -> List[Any]:
        """Run agents in parallel and return all results."""
        tasks = [agent.run(input_data) for agent in self.agents]
        results = await asyncio.gather(*tasks)
        return list(results)


class LoopAgent(Agent):
    """
    ADK-compatible Loop agent for iterative refinement.
    
    Usage:
        loop = LoopAgent(
            name="refiner",
            agent=agent,
            max_iterations=5
        )
        result = await loop.run(input_data)
    """
    
    def __init__(self, name: str, agent: Agent, max_iterations: int = 5):
        super().__init__(name)
        self.agent = agent
        self.max_iterations = max_iterations
    
    async def run(self, input_data: Any) -> Any:
        """Run agent iteratively until max iterations."""
        result = input_data
        for i in range(self.max_iterations):
            result = await self.agent.run(result)
        return result


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


# Export all classes
__all__ = [
    "GeminiModel",
    "LLMAgent",
    "Agent",
    "SequentialAgent",
    "ParallelAgent",
    "LoopAgent",
    "Tool"
]
