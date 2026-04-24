import os
import json, re
from .openrouter_client import OpenRouterClient
from flask import current_app

class YieldPredictor:
    """Harvest yield estimation using OpenRouter."""

    def __init__(self):
        import joblib
        model_path = os.path.join(os.getcwd(), 'ml_models', 'yield_model.pkl')
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            self.model = None

    def predict(self, crop, area, state, district, soil_type, irrigation):
        """Yield Prediction using OpenRouter."""
        api_key = current_app.config.get('OPENROUTER_API_KEY')
        client = OpenRouterClient(api_key=api_key)

        system_instruction = "You are a PhD Agronomy Expert. Output JSON ONLY. Accurate estimations for Indian conditions."
        user_prompt = f"""
        Predict yield and profit for:
        - Crop: {crop}
        - Area: {area} acres
        - Location: {district}, {state}
        - Soil: {soil_type}
        - Irrigation: {irrigation}
        
        JSON fields: yield_per_acre, total_yield, cost_of_cultivation, estimated_market_price, total_revenue, estimated_profit, confidence_score.
        Values must be PURE NUMBERS.
        """

        response_text = client.generate_content(
            prompt=user_prompt,
            system_instruction=system_instruction,
            temperature=0.7
        )

        if response_text:
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match: 
                try:
                    clean_str = match.group(0)
                    clean_str = re.sub(r'([:])\s*[₹$]\s*', r'\1', clean_str) 
                    return json.loads(clean_str)
                except: pass
        return {}

    def get_improvement_suggestions(self, crop, soil, irrigation):
        """Get 3 expert tips using OpenRouter."""
        api_key = current_app.config.get('OPENROUTER_API_KEY')
        if not api_key: return ["Use better fertilizers", "Improve irrigation", "Check soil pH"]

        client = OpenRouterClient(api_key=api_key)
        prompt = f"Provide 3 professional agronomy tips to improve {crop} yield on {soil} soil with {irrigation}. Short & actionable."
        
        response_text = client.generate_content(prompt=prompt)

        if response_text:
            tips = [tip.strip() for tip in response_text.split('\n') if tip.strip() and (tip[0].isdigit() or tip[0] == '-' or tip[0] == '*')]
            if tips: return tips[:3]

        return ["Sample soil every season", "Use certified seeds", "Manage water efficiently"]
