# indexing/context_generator.py

import requests
import json
import time

# Configuration for Local LLaMA (Ollama)
LLM_API_URL = "http://localhost:11434/api/generate"

# ✅ CONFIRMING 0.5B MODEL HERE
MODEL_NAME = "qwen2.5:0.5b" 

class ContextGenerator:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    def generate_context(self, document_text: str, chunk_text: str) -> str:
        """
        Generates a succinct context for the chunk based on the document.
        """
        # Limit input to avoid OOM on 8GB RAM
        truncated_doc = document_text[:2500] 
        
        prompt = f"""
        <document>
        {truncated_doc}
        ...
        </document>
        
        <chunk>
        {chunk_text}
        </chunk>
        
        Task: Give a short (1 sentence) context to situate this chunk within the overall document for search retrieval. 
        Answer only with the context.
        """
        
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0, 
                "num_predict": 50,
                "num_ctx": 2048
            }
        }

        try:
            response = requests.post(LLM_API_URL, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            return result['response'].strip()
        except Exception as e:
            print(f"⚠️ Context generation failed: {e}")
            return ""