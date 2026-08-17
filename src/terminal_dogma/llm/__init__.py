"""Camada de LLM provider-agnóstica (ADR 0002)."""

from terminal_dogma.llm.base import LLMClient
from terminal_dogma.llm.fake import FakeLLMClient
from terminal_dogma.llm.gemini import GeminiClient
from terminal_dogma.llm.resilient import ResilientLLMClient

__all__ = [
    "FakeLLMClient",
    "GeminiClient",
    "LLMClient",
    "ResilientLLMClient",
]
