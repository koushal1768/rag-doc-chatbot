from fastapi import HTTPException, status
from app.core.config import settings
from app.models.client_config import ClientConfig
from app.services.llm_factory.base import BaseLLMAdapter
from app.services.llm_factory.openai_adapter import OpenAIAdapter
from app.services.llm_factory.gemini_adapter import GeminiAdapter
from app.services.llm_factory.claude_adapter import ClaudeAdapter


class LLMFactory:
    @staticmethod
    def get_adapter(user_config: ClientConfig) -> BaseLLMAdapter:
        """Instantiates the configured LLM adapter, resolving BYOK API keys or system fallbacks."""
        provider = user_config.provider.lower()
        model_name = user_config.model_name

        if provider == "openai":
            api_key = user_config.openai_api_key or settings.OPENAI_API_KEY
            return OpenAIAdapter(model_name=model_name, api_key=api_key)

        elif provider == "gemini":
            api_key = user_config.gemini_api_key or settings.GEMINI_API_KEY
            return GeminiAdapter(model_name=model_name, api_key=api_key)

        elif provider == "claude":
            api_key = user_config.claude_api_key or settings.ANTHROPIC_API_KEY
            return ClaudeAdapter(model_name=model_name, api_key=api_key)

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported LLM provider: '{provider}'. Choose 'openai', 'gemini', or 'claude'."
            )