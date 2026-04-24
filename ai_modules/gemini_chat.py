import os
from .groq_client import GroqClient

class GeminiChatbot:
    """Class to manage AI chatbot conversations using Groq."""

    def __init__(self, api_key=None, model=None):
        self.client = GroqClient(api_key=api_key, model=model)

    def get_response(self, user_message, history=None):
        """Unified AI logic using Groq."""
        system_instruction = "You are BHOOMITRA, a PhD Agricultural Advisor. Provide practical, highly accurate advice for Indian farmers. Keep it professional yet accessible."
        
        # Combine history if available (optional, for contextual chat)
        prompt = user_message
        if history:
            # Simple context concatenation if needed, or pass list to GroqClient
            pass

        response = self.client.generate_content(
            prompt=user_message,
            system_instruction=system_instruction,
            temperature=0.7
        )
        return response
