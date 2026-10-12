from typing import Optional
from openai import OpenAI
from fastapi import HTTPException, status

from app.services.llm_factory.base import BaseLLMAdapter


class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self, model_name: str, api_key: str):
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OpenAI API Key is missing. Please configure it in client settings."
            )
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key)

    def generate_response(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.2,
        context: Optional[str] = None
    ) -> str:
        full_system_content = system_prompt
        if context:
            full_system_content += f"\n\nContext:\n{context}"

        messages = [
            {"role": "system", "content": full_system_content},
            {"role": "user", "content": prompt}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"OpenAI API error: {str(e)}"
            )
