from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMAdapter(ABC):
    """Abstract Base Class for all LLM Provider Adapters."""

    @abstractmethod
    def generate_response(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.2,
        context: Optional[str] = None
    ) -> str:
        """Generates a text completion based on prompt and system context."""
        pass