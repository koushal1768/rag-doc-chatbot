from typing import Optional
from anthropic import Anthropic
from fastapi import HTTPException, status

from app.services.llm_factory.base import BaseLLMAdapter


class ClaudeAdapter(BaseLLMAdapter):
    def __init__(self, model_name: str, api_key: str):
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Anthropic API Key is missing. Please configure it in client settings."
            )
        self.model_name = model_name
        self.client = Anthropic(api_key=api_key)

    def generate_response(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.2,
        context: Optional[str] = None
    ) -> str:
        full_system_prompt = system_prompt
        if context:
            full_system_prompt += f"\n\nContext:\n{context}"

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=2048,
                temperature=temperature,
                system=full_system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Claude API error: {str(e)}"
            )