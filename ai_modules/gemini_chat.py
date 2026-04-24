import time
import os
from .openrouter_client import OpenRouterClient

class GeminiChatbot:
    """Class to manage AI chatbot conversations using OpenRouter."""

    def __init__(self, api_key, model=None):
        # We reuse the parameter name api_key for compatibility, 
        # but it will be the OpenRouter API Key.
        if not api_key:
            raise ValueError("API Key is required.")
        self.client = OpenRouterClient(api_key=api_key, model=model)

    def get_response(self, user_message, history=None):
        """Unified AI logic using OpenRouter."""
        system_instruction = "You are BHOOMITRA, a PhD Agricultural Advisor. Provide practical, highly accurate advice for Indian farmers. Keep it professional yet accessible."
        
        response = self.client.generate_content(
            prompt=user_message,
            system_instruction=system_instruction,
            temperature=0.7
        )
        return response
