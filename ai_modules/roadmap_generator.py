from .openrouter_client import OpenRouterClient
import os

class RoadmapGenerator:
    """Class to generate a smart farming roadmap using OpenRouter."""

    def __init__(self, api_key):
        # api_key is OpenRouter API Key
        self.api_key = api_key

    def generate_roadmap(self, crop, soil, water, location):
        """Generate roadmap using OpenRouter."""
        system_instruction = "You are a PhD Agronomist. Generate a professional high-impact farming roadmap in CLEAN MARKDOWN. Use headers (#), bullet points, and tables (| Month | Activity |) for timelines. Avoid using double hashtags like ### ###."
        user_prompt = f"Plan for: {crop} in {soil} soil with {water} water at {location}. Include a detailed 12-month calendar table, specific soil prep steps, and scaling strategy. FORMAT AS GITHUB FLAVORED MARKDOWN."

        client = OpenRouterClient(api_key=self.api_key)
        res = client.generate_content(
            prompt=user_prompt,
            system_instruction=system_instruction,
            temperature=0.7
        )
        
        return res if res else "BHOOMITRA AI is currently under heavy load. Please try again soon."
