"""Fake scriptado de LLM para testes: sem rede, determinístico."""

from collections.abc import Mapping


class FakeLLMClient:
    """Retorna respostas associadas a substrings do prompt."""

    def __init__(self, responses: Mapping[str, str] | None = None, default: str = "") -> None:
        raise NotImplementedError

    async def complete(self, prompt: str) -> str:
        raise NotImplementedError
