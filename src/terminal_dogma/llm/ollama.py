"""Adaptador Ollama via API HTTP local para o Protocol ``LLMClient``."""

import os
from typing import Any

import httpx

from terminal_dogma.domain.exceptions import (
    ATFieldInterference,
    CentralDogmaLockdown,
)

_DEFAULT_MODEL = "llama3.2"
_DEFAULT_HOST = "http://localhost:11434"
_DEFAULT_TIMEOUT = 120.0


class OllamaClient:
    """Cliente para modelos locais rodando no Ollama via API REST assíncrona."""

    def __init__(
        self,
        model: str = _DEFAULT_MODEL,
        host: str = _DEFAULT_HOST,
        temperature: float = 0.3,
        timeout: float = _DEFAULT_TIMEOUT,
        agent_name: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.model = model
        self.host = host.rstrip("/")
        self.temperature = temperature
        self.timeout = timeout
        self.agent_name = agent_name
        self._client = client

    @classmethod
    def from_env(cls, **kwargs: Any) -> "OllamaClient":
        """Instancia o cliente a partir das variáveis de ambiente."""
        model = os.environ.get("OLLAMA_MODEL", _DEFAULT_MODEL)
        host = os.environ.get("OLLAMA_HOST", _DEFAULT_HOST)
        return cls(model=model, host=host, **kwargs)

    async def complete(self, prompt: str) -> str:
        """Envia o prompt para a API do Ollama e retorna a resposta de texto."""
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self.temperature},
        }

        try:
            if self._client is not None:
                response = await self._client.post(url, json=payload, timeout=self.timeout)
                return self._handle_response(response)

            async with httpx.AsyncClient(timeout=self.timeout) as http_client:
                response = await http_client.post(url, json=payload)
                return self._handle_response(response)

        except (ATFieldInterference, CentralDogmaLockdown):
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise ATFieldInterference(agent_name=self.agent_name or "Ollama") from e
            raise CentralDogmaLockdown(subsystem=self.agent_name or "Ollama") from e
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
            raise CentralDogmaLockdown(
                subsystem=f"Servidor Ollama inacessível em {self.host}. "
                "Execute 'ollama serve' no terminal para iniciar o serviço local."
            ) from e
        except Exception as e:
            raise CentralDogmaLockdown(subsystem=f"Ollama ({e})") from e

    def _handle_response(self, response: httpx.Response) -> str:
        if response.status_code == 429:
            raise ATFieldInterference(agent_name=self.agent_name or "Ollama")
        if response.is_error:
            raise CentralDogmaLockdown(subsystem=self.agent_name or "Ollama")
        data = response.json()
        if isinstance(data, dict):
            return str(data.get("response", ""))
        return ""
