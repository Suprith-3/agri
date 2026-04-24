import cv2
import os
import time
from .openrouter_client import OpenRouterClient
from flask import current_app

class DiseaseDetector:
    """Class to handle crop disease detection using OpenRouter."""

    def __init__(self):
        import joblib
        # Load the pre-trained model
        model_path = os.path.join(os.getcwd(), 'ml_models', 'disease_model.pkl')
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            self.model = None

    def predict(self, image_path):
        """Sequential Disease Identification using OpenRouter Vision."""
        api_key = current_app.config.get('OPENROUTER_API_KEY')
        if not api_key: return "Key Missing", 0.0
            
        prompt = """
        Analyze this agricultural image. 
        1. If it's NOT a plant, say 'Not Agriculture'.
        2. If it's a healthy plant, say 'Healthy'.
        3. If it's diseased, identify the disease name clearly.
        Output ONLY the name or status.
        """
        
        client = OpenRouterClient(api_key=api_key)
        response_text = client.generate_content(prompt=prompt, image_path=image_path)

        if response_text:
            rt = response_text.strip()
            if "Not Agriculture" in rt: return "Not Agriculture", 0.99
            if "Healthy" in rt.capitalize(): return "Healthy", 0.95
            return rt, 0.92
        
        return "Detection Error: Cloud network unstable.", 0.0

    def get_ai_treatment(self, disease_name, confidence):
        """Treatment advice using OpenRouter."""
        if disease_name in ["Not Agriculture", "Detection Error", "Healthy"]:
            return f"Status: {disease_name}. No treatment calculation needed."
            
        api_key = current_app.config.get('OPENROUTER_API_KEY')
        prompt = f"""
        You are a PhD Plant Pathologist. Provide a detailed treatment plan for {disease_name}.
        Confidence in diagnosis: {confidence*100:.1f}%.
        Structure:
        - **Cause**: Pathogen details
        - **Symptoms**: What to look for
        - **Organic Control**: Natural remedies
        - **Chemical Control**: Recommended fungicides/pesticides
        - **Prevention**: Long-term field management
        Markdown format.
        """

        client = OpenRouterClient(api_key=api_key)
        res = client.generate_content(prompt=prompt)
        return res if res else "Diagnosis complete, but treatment consultation timed out."
