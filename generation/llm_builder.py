# generation/llm_builder.py

import requests
import json

class LLMBuilder:
    def __init__(self, model_name="qwen2.5:3b", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/generate"
    
    def generate(self, prompt: str, model_name: str = None, max_tokens=500) -> str:
        """
        Generate answer using Ollama
        """
        target_model = model_name if model_name else self.model_name

        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "60m", 
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.7,
                # OPTIMIZATION: Reduced context window to 2048 to prevent RAM swapping
                "num_ctx": 2048 
            }
        }
        
        try:
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "No response generated")
            
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Ollama: {str(e)}"