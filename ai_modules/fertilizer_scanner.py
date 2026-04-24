import os
from .groq_client import GroqClient
from flask import current_app

class FertilizerScanner:
    """Class to identify fertilizer using Groq Vision."""

    def __init__(self, api_key=None):
        self.api_key = api_key

    def scan(self, image_path):
        """Analyze fertilizer image."""
        prompt = """
        Analyze this agricultural product image with high accuracy.
        Provide a detailed report in a clean, professional format WITHOUT using any markdown symbols like # or *.
        Format it exactly as a numbered list like this:
        1. PRODUCT NAME: (Name and Type)
        2. NPK CONTENT: (Ratio or composition)
        3. SAFETY: (Precautions and handling)
        4. CROPS: (Recommended usage)
        5. DOSAGE: (Instructions per acre)
        6. APPLICATION: (Method of use)
        
        Keep each point on a new line with a double space between points.
        """
        
        client = GroqClient(api_key=self.api_key)
        response_text = client.generate_content(prompt=prompt, image_path=image_path)
        
        if response_text:
            # Aggressively remove all markdown symbols and extra hashes
            clean_text = response_text.replace("#", "").replace("*", "").strip()
            # Ensure double spacing between numbered points for arrangement
            import re
            clean_text = re.sub(r'(\d\.)', r'\n\1', clean_text)
            return clean_text.strip()
        
        return "Scanner unavailable. Please try again."
