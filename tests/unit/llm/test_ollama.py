"""Testes do adaptador Ollama via API HTTP local (sem rede real)."""

import httpx
import pytest

from terminal_dogma.domain.exceptions import ATFieldInterference, CentralDogmaLockdown
from terminal_dogma.llm.ollama import OllamaClient


def _make_transport(handler):
    return httpx.MockTransport(handler)


async def test_complete_retorna_resposta_do_ollama():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/generate"
        return httpx.Response(200, json={"response": "Análise gerada pelo modelo local."})

    async with httpx.AsyncClient(transport=_make_transport(handler)) as http_client:
        client = OllamaClient(
            model="llama3.2",
            host="http://localhost:11434",
            client=http_client,
        )
        result = await client.complete("Qual o plano?")
        assert result == "Análise gerada pelo modelo local."


async def test_complete_envia_payload_correto():
    recorded_requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        recorded_requests.append(request)
        return httpx.Response(200, json={"response": "OK"})

    async with httpx.AsyncClient(transport=_make_transport(handler)) as http_client:
        client = OllamaClient(
            model="mistral",
            host="http://custom-host:11434",
            temperature=0.4,
            client=http_client,
        )
        await client.complete("Prompt de teste")

    assert len(recorded_requests) == 1
    req = recorded_requests[0]
    assert req.url == "http://custom-host:11434/api/generate"
    import json

    body = json.loads(req.content.decode("utf-8"))
    assert body["model"] == "mistral"
    assert body["prompt"] == "Prompt de teste"
    assert body["stream"] is False
    assert body["options"]["temperature"] == 0.4


async def test_rate_limit_429_vira_at_field_interference():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "too many requests"})

    async with httpx.AsyncClient(transport=_make_transport(handler)) as http_client:
        client = OllamaClient(client=http_client, agent_name="MELCHIOR-01")
        with pytest.raises(ATFieldInterference) as exc_info:
            await client.complete("prompt")
        assert exc_info.value.agent_name == "MELCHIOR-01"


async def test_erro_de_conexao_vira_central_dogma_lockdown():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Connection refused")

    async with httpx.AsyncClient(transport=_make_transport(handler)) as http_client:
        client = OllamaClient(client=http_client)
        with pytest.raises(CentralDogmaLockdown) as exc_info:
            await client.complete("prompt")
        assert "Ollama" in exc_info.value.subsystem


async def test_timeout_vira_central_dogma_lockdown():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Read timed out")

    async with httpx.AsyncClient(transport=_make_transport(handler)) as http_client:
        client = OllamaClient(client=http_client)
        with pytest.raises(CentralDogmaLockdown):
            await client.complete("prompt")


async def test_erro_500_vira_central_dogma_lockdown():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "model not found"})

    async with httpx.AsyncClient(transport=_make_transport(handler)) as http_client:
        client = OllamaClient(client=http_client)
        with pytest.raises(CentralDogmaLockdown):
            await client.complete("prompt")


async def test_resposta_sem_campo_response_retorna_vazio():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    async with httpx.AsyncClient(transport=_make_transport(handler)) as http_client:
        client = OllamaClient(client=http_client)
        assert await client.complete("prompt") == ""


def test_from_env(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5")
    monkeypatch.setenv("OLLAMA_HOST", "http://192.168.1.100:11434")

    client = OllamaClient.from_env()
    assert client.model == "qwen2.5"
    assert client.host == "http://192.168.1.100:11434"


async def test_complete_sem_client_injetado(monkeypatch):
    original_cls = httpx.AsyncClient

    def mock_async_client(*args, **kwargs):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"response": "Sucesso default client"})

        return original_cls(transport=_make_transport(handler))

    monkeypatch.setattr(httpx, "AsyncClient", mock_async_client)
    client = OllamaClient(model="llama3.2")
    res = await client.complete("prompt")
    assert res == "Sucesso default client"


async def test_erro_inesperado_vira_central_dogma_lockdown():
    def handler(request: httpx.Request) -> httpx.Response:
        raise RuntimeError("Erro bizarro")

    async with httpx.AsyncClient(transport=_make_transport(handler)) as http_client:
        client = OllamaClient(client=http_client)
        with pytest.raises(CentralDogmaLockdown):
            await client.complete("prompt")
