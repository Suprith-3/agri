import requests
import json
import time
import base64
from flask import current_app

class GroqClient:
    """Ultra-fast AI client using Groq API (OpenAI Compatible)."""
    
    _session = None

    def __init__(self, api_key=None, model=None):
        import os
        # Use provided key, or try current_app config, or fallback to environment variable
        # This prevents RuntimeError when instantiated outside app context at import time
        try:
            self.api_key = api_key or current_app.config.get('GROQ_API_KEY')
            self.model = model or current_app.config.get('GROQ_MODEL', 'llama-3.3-70b-versatile')
        except RuntimeError:
            self.api_key = api_key or os.getenv('GROQ_API_KEY')
            self.model = model or os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
            
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        
        if GroqClient._session is None:
            GroqClient._session = requests.Session()

    def generate_content(self, prompt, system_instruction=None, temperature=0.7, image_path=None):
        """Execute ultra-fast inference on Groq."""
        if not self.api_key:
            return "Groq API Key is missing. Please check your .env file."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        
        # Determine model - use vision model if image is provided
        current_model = self.model
        if image_path:
            current_model = "meta-llama/llama-4-scout-17b-16e-instruct" # New Llama 4 Multimodal
            try:
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    })
            except Exception as e:
                print(f"[Groq] Image Error: {e}")
                messages.append({"role": "user", "content": prompt})
        else:
            messages.append({"role": "user", "content": prompt})

        start_time = time.time()
        try:
            payload = {
                "model": current_model if not image_path else "llama-3.2-11b-vision-preview",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 1024
            }
            
            response = self._session.post(
                self.base_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=15,
                verify=True # Change to False ONLY if you have SSL certificate issues locally
            )
            
            if response.status_code == 200:
                json_data = response.json()
                latency = time.time() - start_time
                print(f"[Groq Speed] {current_model} responded in {latency:.2f}s")
                return json_data['choices'][0]['message']['content']
            elif response.status_code == 401:
                return "AI Error: Invalid Groq API Key. Please update your .env file."
            elif response.status_code == 429:
                return "AI Error: Groq Rate Limit reached. Please wait a moment."
            else:
                print(f"[Groq Error] {response.status_code}: {response.text}")
                return f"AI Error: Groq returned {response.status_code}"
                
        except Exception as e:
            print(f"[Groq Connection Error] {str(e)}")
            return "BHOOMITRA AI (Groq) is currently unreachable. Check your internet or API key."
