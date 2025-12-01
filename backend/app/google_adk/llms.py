"""
Google ADK LLMs - Compatibility Layer

Provides model classes compatible with ADK interface.
"""

import google.generativeai as genai
import asyncio


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


__all__ = ["GeminiModel"]
