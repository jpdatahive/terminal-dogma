"""Testes do adaptador Gemini com o client do SDK mockado (sem rede).

Os erros usados são instâncias reais das classes tipadas do SDK
(``google.genai.errors``), garantindo que a tradução não depende de
string matching.
"""

import sys
from types import SimpleNamespace

import httpx
import pytest
from google.genai import errors

from terminal_dogma.domain.exceptions import ATFieldInterference, CentralDogmaLockdown
from terminal_dogma.llm import GeminiClient


class FakeModels:
    """Simula ``client.aio.models`` do SDK google-genai."""

    def __init__(self, result=None, exc: Exception | None = None):
        self._result = result
        self._exc = exc
        self.calls: list[dict] = []

    async def generate_content(self, *, model, contents, config):
        self.calls.append({"model": model, "contents": contents, "config": config})
        if self._exc is not None:
            raise self._exc
        return self._result


def _client(models: FakeModels | None = None, **kwargs):
    models = models or FakeModels(result=SimpleNamespace(text="resposta"))
    genai_client = SimpleNamespace(aio=SimpleNamespace(models=models))
    return GeminiClient(api_key="fake-key", client=genai_client, **kwargs), models


async def test_complete_retorna_texto_da_resposta():
    client, _ = _client()
    assert await client.complete("prompt") == "resposta"


async def test_complete_passa_modelo_prompt_e_temperatura():
    client, models = _client(model="gemini-x", temperature=0.2)
    await client.complete("meu prompt")

    call = models.calls[0]
    assert call["model"] == "gemini-x"
    assert call["contents"] == "meu prompt"
    assert call["config"].temperature == 0.2


async def test_resposta_sem_texto_retorna_string_vazia():
    client, _ = _client(models=FakeModels(result=SimpleNamespace(text=None)))
    assert await client.complete("prompt") == ""


async def test_rate_limit_429_vira_at_field_interference_com_nome_do_agente():
    exc = errors.ClientError(
        code=429,
        response_json={"error": {"status": "RESOURCE_EXHAUSTED", "message": "quota"}},
    )
    client, _ = _client(models=FakeModels(exc=exc), agent_name="MELCHIOR-01")

    with pytest.raises(ATFieldInterference) as exc_info:
        await client.complete("prompt")
    assert exc_info.value.agent_name == "MELCHIOR-01"


async def test_server_error_vira_central_dogma_lockdown():
    exc = errors.ServerError(
        code=500, response_json={"error": {"status": "INTERNAL", "message": "boom"}}
    )
    client, _ = _client(models=FakeModels(exc=exc))

    with pytest.raises(CentralDogmaLockdown):
        await client.complete("prompt")


async def test_client_error_nao_429_vira_lockdown():
    exc = errors.ClientError(
        code=403, response_json={"error": {"status": "PERMISSION_DENIED", "message": "key"}}
    )
    client, _ = _client(models=FakeModels(exc=exc))

    with pytest.raises(CentralDogmaLockdown):
        await client.complete("prompt")


async def test_erro_de_conexao_vira_lockdown():
    client, _ = _client(models=FakeModels(exc=httpx.ConnectError("no route to host")))

    with pytest.raises(CentralDogmaLockdown):
        await client.complete("prompt")


async def test_erro_desconhecido_vira_lockdown_conservador():
    client, _ = _client(models=FakeModels(exc=RuntimeError("inesperado")))

    with pytest.raises(CentralDogmaLockdown):
        await client.complete("prompt")


def test_sem_sdk_instalado_erro_indica_o_extra(monkeypatch):
    monkeypatch.setitem(sys.modules, "google.genai", None)
    monkeypatch.setitem(sys.modules, "google", None)

    with pytest.raises(ImportError, match="gemini"):
        GeminiClient(api_key="x")
