
from typing import Optional
from google import genai
from google.genai import types
from fastapi import HTTPException, status

from app.services.llm_factory.base import BaseLLMAdapter


class GeminiAdapter(BaseLLMAdapter):
    def __init__(self, model_name: str, api_key: str):
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gemini API Key is missing. Please configure it in client settings."
            )
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)

    def generate_response(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.2,
        context: Optional[str] = None
    ) -> str:
        full_system_instruction = system_prompt
        if context:
            full_system_instruction += f"\n\nContext:\n{context}"

        config = types.GenerateContentConfig(
            system_instruction=full_system_instruction,
            temperature=temperature
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Gemini API error: {str(e)}"
            )
