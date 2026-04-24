import requests
import numpy as np
import json
from .openrouter_client import OpenRouterClient

class CropRecommender:
    """Location-based intelligent crop recommendation logic using OpenRouter."""

    def __init__(self, weather_api_key=None, gemini_api_key=None):
        self.weather_api_key = weather_api_key
        # We store gemini_api_key but it's now actually the OpenRouter API Key
        self.gemini_api_key = gemini_api_key
        self.rules = {
            ('Loamy', 'Abundant', 'Rainy'): ['Rice', 'Sugarcane', 'Cotton'],
            ('Black', 'Moderate', 'Rainy'): ['Cotton', 'Soybean', 'Jowar'],
            ('Sandy', 'Scarce', 'Winter'): ['Groundnut', 'Mustard', 'Bajra'],
            ('Alluvial', 'Abundant', 'Winter'): ['Wheat', 'Gram', 'Mustard'],
            ('Red', 'Moderate', 'Rainy'): ['Maize', 'Groundnut', 'Pulses'],
            ('Clay', 'Abundant', 'Rainy'): ['Rice', 'Jute', 'Sugarcane'],
            ('Loamy', 'Moderate', 'Winter'): ['Wheat', 'Barley', 'Peas'],
            ('Sandy', 'Moderate', 'Summer'): ['Watermelon', 'Cucumber', 'Muskmelon'],
        }

    def get_weather(self, lat, lng):
        """Fetch current weather for enrichment."""
        if not self.weather_api_key:
            return None
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={self.weather_api_key}&units=metric"
        try:
            r = requests.get(url, timeout=10)
            return r.json()
        except:
            return None

    def recommend(self, soil_type, water, season, lat, lng):
        """Smart-Sequential Crop Recommendation using Groq."""
        if not self.gemini_api_key:
            return self._fallback_recommend(soil_type, water, season)

        prompt = f"""
        You are a Senior Agronomist specialized in Indian agriculture. Analyze:
        - GPS: ({lat}, {lng}), Soil: {soil_type}, Water: {water}, Season: {season}
        Provide 5 tailored crops. Return valid JSON only, either a list of 5 objects or an object with a 'crops' key.
        Each object MUST have: name, score, yield_range, water_req, demand, profit, planting_month.
        """
        
        client = GroqClient(api_key=self.gemini_api_key)
        response_text = client.generate_content(prompt=prompt, temperature=0.7)

        try:
            # Basic cleanup if Markdown is returned
            clean_text = response_text.replace('```json', '').replace('```', '').strip()
            res = json.loads(clean_text)
            if isinstance(res, list): return res[:5]
            if isinstance(res, dict) and 'crops' in res: return res['crops'][:5]
            if isinstance(res, dict): return [res] # Just in case it's one object
        except Exception as e:
            print(f"[Crop AI] Error parsing response: {str(e)}")

        return self._fallback_recommend(soil_type, water, season)

    def _fallback_recommend(self, soil_type, water, season):
        """Rule-based fallback for reliability."""
        matches = self.rules.get((soil_type, water, season), ['Maize', 'Pulses', 'Oilseeds'])
        recommendations = []
        for crop in matches:
            recommendations.append({
                'name': crop,
                'score': 85 + np.random.randint(0, 15),
                'yield_range': '15-25 quintals/acre',
                'water_req': water,
                'demand': 'High',
                'profit': '₹40,000 - ₹60,000 / acre',
                'planting_month': 'June-July' if season == 'Rainy' else 'Oct-Nov'
            })
        return recommendations[:5]
