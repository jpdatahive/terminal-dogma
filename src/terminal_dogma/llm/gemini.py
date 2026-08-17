"""Adaptador Gemini via SDK oficial ``google-genai`` (extra opcional)."""

from typing import Any

_DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiClient:
    """``LLMClient`` para o Google Gemini.

    O SDK é importado de forma lazy (instalação base não o exige) e o client
    é injetável para testes sem rede.
    """

    def __init__(
        self,
        api_key: str,
        *,
        model: str = _DEFAULT_MODEL,
        temperature: float = 0.7,
        agent_name: str = "GEMINI",
        client: Any | None = None,
    ) -> None:
        raise NotImplementedError

    async def complete(self, prompt: str) -> str:
        raise NotImplementedError
