"""Testes do ResilientLLMClient (timeout + retry com backoff exponencial)."""

import asyncio
from collections.abc import Callable

import pytest

from terminal_dogma.domain.exceptions import ATFieldInterference, CentralDogmaLockdown
from terminal_dogma.llm import FakeLLMClient, ResilientLLMClient


class FlakyClient:
    """Cliente que falha ``failures`` vezes e depois responde ``result``."""

    def __init__(self, failures: int, exc_factory: Callable[[], Exception], result: str = "ok"):
        self._failures = failures
        self._exc_factory = exc_factory
        self._result = result
        self.attempts = 0

    async def complete(self, prompt: str) -> str:
        self.attempts += 1
        if self.attempts <= self._failures:
            raise self._exc_factory()
        return self._result


class FakeSleep:
    """Sleep injetável: registra os delays sem esperar de verdade."""

    def __init__(self) -> None:
        self.delays: list[float] = []

    async def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)


async def test_sucesso_sem_nenhum_retry():
    sleep = FakeSleep()
    client = ResilientLLMClient(FakeLLMClient(default="ok"), sleep=sleep)
    assert await client.complete("prompt") == "ok"
    assert sleep.delays == []


async def test_recupera_apos_rate_limits_com_backoff_exponencial():
    sleep = FakeSleep()
    flaky = FlakyClient(failures=2, exc_factory=ATFieldInterference)
    client = ResilientLLMClient(flaky, max_retries=2, base_delay_seconds=0.5, sleep=sleep)

    assert await client.complete("prompt") == "ok"
    assert flaky.attempts == 3
    assert sleep.delays == [0.5, 1.0]


async def test_esgota_retries_e_propaga_o_ultimo_erro():
    flaky = FlakyClient(failures=99, exc_factory=lambda: ATFieldInterference("CASPER-03"))
    client = ResilientLLMClient(flaky, max_retries=2, sleep=FakeSleep())

    with pytest.raises(ATFieldInterference) as exc_info:
        await client.complete("prompt")
    assert exc_info.value.agent_name == "CASPER-03"
    assert flaky.attempts == 3


async def test_timeout_vira_central_dogma_lockdown():
    class SlowClient:
        async def complete(self, prompt: str) -> str:
            await asyncio.sleep(10)
            return "tarde demais"

    client = ResilientLLMClient(
        SlowClient(), max_retries=1, timeout_seconds=0.01, sleep=FakeSleep()
    )
    with pytest.raises(CentralDogmaLockdown):
        await client.complete("prompt")


async def test_lockdown_transiente_tambem_tem_retry():
    flaky = FlakyClient(failures=1, exc_factory=lambda: CentralDogmaLockdown("REDE"))
    client = ResilientLLMClient(flaky, max_retries=1, sleep=FakeSleep())
    assert await client.complete("prompt") == "ok"
    assert flaky.attempts == 2
