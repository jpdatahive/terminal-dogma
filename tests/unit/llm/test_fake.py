"""Testes do FakeLLMClient scriptado."""

from terminal_dogma.llm import FakeLLMClient


async def test_retorna_resposta_associada_a_substring_do_prompt():
    fake = FakeLLMClient(responses={"MELCHIOR": "VOTO: POSITIVO"}, default="?")
    assert await fake.complete("Análise de MELCHIOR-01 sobre X") == "VOTO: POSITIVO"


async def test_sem_match_retorna_default():
    fake = FakeLLMClient(responses={"nada": "x"}, default="resposta padrão")
    assert await fake.complete("prompt qualquer") == "resposta padrão"


async def test_primeira_substring_encontrada_vence():
    fake = FakeLLMClient(responses={"alfa": "A", "alfa beta": "AB"})
    assert await fake.complete("alfa beta gama") == "A"


async def test_registra_todas_as_chamadas_em_calls():
    fake = FakeLLMClient()
    await fake.complete("um")
    await fake.complete("dois")
    assert fake.calls == ["um", "dois"]
