"""
GROQ API Client wrapper for AI calls
"""
from groq import Groq
from app.core.config import settings
from typing import Optional
import json


class GroqClient:
    def __init__(self):
        self.client = None
        if settings.GROQ_API_KEY:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def chat_completion(
        self,
        messages: list[dict],
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.0,
        max_tokens: int = 2048,
        response_format: Optional[dict] = None
    ) -> str:
        """
        Send a chat completion request to GROQ.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use
            temperature: Sampling temperature (0 for deterministic)
            max_tokens: Max tokens in response
            response_format: Optional format spec (e.g., {"type": "json_object"})
        
        Returns:
            The response content as string
        """
        if not self.client:
            raise RuntimeError("GROQ client not initialized. Check GROQ_API_KEY.")
        
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def parse_json_response(self, response: str) -> dict:
        """
        Parse JSON from response, handling potential markdown code blocks.
        """
        content = response.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        
        if content.endswith("```"):
            content = content[:-3]
        
        return json.loads(content.strip())


# Singleton instance
groq_client = GroqClient()
