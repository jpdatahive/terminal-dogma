"""Adaptador Gemini via SDK oficial ``google-genai`` (extra opcional).

Tradução de erros por tipo, nunca por string matching:

- ``APIError`` 429 / ``RESOURCE_EXHAUSTED`` → ``ATFieldInterference``
- demais ``APIError`` (4xx/5xx) → ``CentralDogmaLockdown``
- erros de rede do ``httpx`` → ``CentralDogmaLockdown``
- qualquer outro erro → ``CentralDogmaLockdown`` (postura conservadora)
"""

from typing import Any

from terminal_dogma.domain.exceptions import (
    ATFieldInterference,
    CentralDogmaLockdown,
    DogmaSystemException,
)

_DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiClient:
    """``LLMClient`` para o Google Gemini.

    O SDK é importado de forma lazy para que a instalação base não o exija
    (instale com ``uv sync --extra gemini``). O ``client`` injetável permite
    testes sem rede.
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
        try:
            from google import genai
            from google.genai import errors, types
        except ImportError as exc:
            raise ImportError(
                "O adaptador Gemini requer o SDK oficial google-genai. "
                "Instale com: uv sync --extra gemini"
            ) from exc

        self._model = model
        self._temperature = temperature
        self._agent_name = agent_name
        self._types = types
        self._api_error = errors.APIError
        self._client = client if client is not None else genai.Client(api_key=api_key)

    async def complete(self, prompt: str) -> str:
        config = self._types.GenerateContentConfig(temperature=self._temperature)
        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config,
            )
        except Exception as exc:
            raise self._translate(exc) from exc

        text: object = getattr(response, "text", None)
        return text if isinstance(text, str) else ""

    def _translate(self, exc: Exception) -> DogmaSystemException:
        if isinstance(exc, self._api_error):
            code = getattr(exc, "code", None)
            status = getattr(exc, "status", None)
            if code == 429 or status == "RESOURCE_EXHAUSTED":
                return ATFieldInterference(self._agent_name)
            return CentralDogmaLockdown(self._agent_name)
        # Erros de rede/transporte (httpx) e qualquer surpresa: lockdown.
        return CentralDogmaLockdown(self._agent_name)
