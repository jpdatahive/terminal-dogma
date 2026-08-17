"""Fake scriptado de LLM para testes: sem rede, determinístico."""

from collections.abc import Mapping


class FakeLLMClient:
    """Retorna respostas associadas a substrings do prompt.

    A primeira substring do mapeamento encontrada no prompt define a
    resposta; sem match, retorna ``default``. Todos os prompts recebidos
    ficam registrados em ``calls`` para asserções.
    """

    def __init__(self, responses: Mapping[str, str] | None = None, default: str = "") -> None:
        self._responses = dict(responses or {})
        self._default = default
        self.calls: list[str] = []

    async def complete(self, prompt: str) -> str:
        self.calls.append(prompt)
        for needle, response in self._responses.items():
            if needle in prompt:
                return response
        return self._default
