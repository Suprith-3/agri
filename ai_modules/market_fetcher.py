import json
import re
from .groq_client import GroqClient
from datetime import datetime

class MarketFetcher:
    """Helper to fetch 'real' APMC market rates using Groq."""

    def __init__(self, api_key=None):
        self.api_key = api_key

    def fetch_latest_rates(self, state="Karnataka", crop=None):
        """Market rate retrieval using Groq."""
        system_instruction = f"You are a real-time Agricultural Market Data API. Output JSON ONLY for {state} APMC rates. Use recent realistic data."
        user_prompt = f"Latest Mandi rates (April 2026) for {crop or 'major crops'} in {state}, India. JSON array: crop, mandi, price, arrival_quantity."

        client = GroqClient(api_key=self.api_key)
        
        try:
            response_text = client.generate_content(
                prompt=user_prompt,
                system_instruction=system_instruction,
                temperature=0.7
            )
            
            if response_text:
                match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if match: return json.loads(match.group(0))
        except Exception: 
            pass
        return []
