import os
from .groq_client import GroqClient
from flask import current_app

class FertilizerScanner:
    """Class to identify fertilizer using the latest Groq Llama-4 Scout."""

    def __init__(self, api_key=None):
        self.api_key = api_key

    def scan(self, image_path):
        """Analyze fertilizer image using Groq Llama-4 Scout."""
        prompt = """
        Analyze this agricultural product image. 
        Identify it and provide a detailed report.
        DO NOT use any markdown symbols like # or *.
        Format it as a numbered list:
        1. PRODUCT NAME: 
        2. NPK CONTENT: 
        3. SAFETY: 
        4. CROPS: 
        5. DOSAGE: 
        6. APPLICATION:
        """
        
        client = GroqClient(api_key=self.api_key)
        response_text = client.generate_content(prompt=prompt, image_path=image_path)
        
        if response_text:
            # Clean up all markdown symbols
            clean_text = response_text.replace("#", "").replace("*", "").strip()
            return clean_text
        
        return "Scanner unavailable. Please check your Groq API key."
