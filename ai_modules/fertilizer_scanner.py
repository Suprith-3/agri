import os
from .openrouter_client import OpenRouterClient
from flask import current_app

class FertilizerScanner:
    """Class to identify fertilizer using OpenRouter Vision."""

    def __init__(self, api_key):
        # api_key here is OpenRouter API Key
        self.api_key = api_key

    def scan(self, image_path):
        """Analyze fertilizer image."""
        api_key = self.api_key or current_app.config.get('OPENROUTER_API_KEY')
        if not api_key: return "API Key Missing."

        prompt = """
        You are an expert Agricultural Product Specialist. Analyze this fertilizer image with high accuracy.
        Provide the following details in a clean Markdown format:
        1. **Product Name & Type**
        2. **NPK Ratio** (if visible or known)
        3. **Safe Handling & Precautions**
        4. **Recommended Crops**
        5. **Precise Dosage instructions** per acre/hectare
        6. **Application Method** (Foliar, Basal, etc.)
        Be extremely accurate. 
        """
        
        client = OpenRouterClient(api_key=api_key)
        response_text = client.generate_content(prompt=prompt, image_path=image_path)
        
        return response_text if response_text else "Scanner unavailable. Please try again."
