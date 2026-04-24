import requests
import json
import time
import base64
import os
try:
    import google.generativeai as genai
    HAS_GOOGLE_SDK = True
except ImportError:
    HAS_GOOGLE_SDK = False
from flask import current_app

class OpenRouterClient:
    """A high-performance oriented client with direct Gemini SDK support and fast fallbacks."""
    
    _session = None
    _google_client_initialized = False

    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or current_app.config.get('OPENROUTER_API_KEY')
        self.gemini_key = current_app.config.get('GEMINI_API_KEY')
        self.primary_model = model or current_app.config.get('OPENROUTER_MODEL', 'google/gemini-2.0-flash-exp:free')
        self.gemini_model_name = current_app.config.get('GEMINI_MODEL', 'gemini-1.5-flash')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        if OpenRouterClient._session is None:
            OpenRouterClient._session = requests.Session()
            
        if HAS_GOOGLE_SDK and self.gemini_key and not OpenRouterClient._google_client_initialized:
            try:
                genai.configure(api_key=self.gemini_key)
                OpenRouterClient._google_client_initialized = True
                print("[AI Speed] Native Google SDK Initialized.")
            except Exception as e:
                print(f"[AI Speed] Google SDK Init Failed: {e}")

        # Fast, reliable free models ordered by speed
        self.additional_fallbacks = [
            "google/gemini-2.0-flash-exp:free",
            "google/gemini-flash-1.5-8b:free",
            "openrouter/free",
            "meta-llama/llama-3.1-8b-instruct:free",
            "qwen/qwen-2-7b-instruct:free"
        ]

    def generate_content(self, prompt, system_instruction=None, temperature=0.7, image_path=None):
        """Ultra-fast generation using direct Gemini SDK or optimized OpenRouter routing."""
        
        # 1. FAST PATH: DIRECT NATIVE GEMINI SDK (Bypass OpenRouter)
        if HAS_GOOGLE_SDK and OpenRouterClient._google_client_initialized and "gemini" in self.primary_model.lower():
            start_time = time.time()
            try:
                # Map OpenRouter model names to native names if needed
                # For now, we use the GEMINI_MODEL setting from config
                model = genai.GenerativeModel(
                    model_name=self.gemini_model_name,
                    system_instruction=system_instruction
                )
                
                if image_path:
                    from PIL import Image
                    img = Image.open(image_path)
                    response = model.generate_content([prompt, img], generation_config={"temperature": temperature})
                else:
                    response = model.generate_content(prompt, generation_config={"temperature": temperature})
                
                if response and response.text:
                    latency = time.time() - start_time
                    print(f"[AI Speed] Native Gemini responded in {latency:.2f}s")
                    return response.text
            except Exception as e:
                print(f"[AI Speed] Native Gemini failed: {e}. Falling back to OpenRouter...")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://agrismart.ai",
            "X-Title": "BHOOMITRA",
        }

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        
        if image_path:
            try:
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                    ext = image_path.split('.')[-1].lower()
                    mime_type = f"image/{ext}" if ext in ['png', 'jpg', 'jpeg', 'webp'] else "image/jpeg"
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
                        ]
                    })
            except Exception as e:
                print(f"[AI Speed] Image Error: {e}")
                messages.append({"role": "user", "content": prompt})
        else:
            messages.append({"role": "user", "content": prompt})

        # Priority: Primary -> Specific Fast Fallbacks
        model_queue = [self.primary_model] + [m for m in self.additional_fallbacks if m != self.primary_model]
        
        for model_id in model_queue:
            start_time = time.time()
            try:
                payload = {
                    "model": model_id,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 1000 # Limit tokens for speed
                }
                
                # Shorter timeout for faster failover
                response = self._session.post(
                    self.base_url,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=12 
                )
                
                if response.status_code == 200:
                    json_data = response.json()
                    if 'choices' in json_data and len(json_data['choices']) > 0:
                        latency = time.time() - start_time
                        print(f"[AI Speed] {model_id} responded in {latency:.2f}s")
                        return json_data['choices'][0]['message']['content']
                
                print(f"[AI Speed] {model_id} failed ({response.status_code}). Switching...")
                    
            except Exception as e:
                print(f"[AI Speed] {model_id} connection error. Switching...")
                continue
        
        return "BHOOMITRA AI is responding slowly due to high traffic. Please try again in a moment."

