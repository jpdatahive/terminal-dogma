"""Teste live contra a API real do Gemini.

Skipado por padrão: exige ``GOOGLE_API_KEY`` no ambiente. Rode com:

    GOOGLE_API_KEY=... uv run pytest tests/live -m live
"""

import os

import pytest

from terminal_dogma.llm import GeminiClient

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="GOOGLE_API_KEY não definida"),
]


async def test_gemini_responde_texto_real():
    client = GeminiClient(api_key=os.environ["GOOGLE_API_KEY"])
    response = await client.complete("Responda exatamente: NENHUM VETO")
    assert isinstance(response, str)
    assert response.strip()
