"""Decorator de resiliência: timeout por chamada + retry com backoff."""

import asyncio
from collections.abc import Awaitable, Callable

from terminal_dogma.domain.exceptions import (
    ATFieldInterference,
    CentralDogmaLockdown,
    DogmaSystemException,
)
from terminal_dogma.llm.base import LLMClient


class ResilientLLMClient:
    """Envolve um ``LLMClient`` com timeout e retries exponenciais.

    Retenta interferências de Campo AT (rate limit) e lockdowns transitórios
    com backoff ``base * 2**attempt``. O ``sleep`` é injetável para que os
    testes não esperem de verdade. Timeout de chamada vira
    ``CentralDogmaLockdown``.
    """

    def __init__(
        self,
        inner: LLMClient,
        *,
        max_retries: int = 2,
        timeout_seconds: float = 30.0,
        base_delay_seconds: float = 0.5,
        sleep: Callable[[float], Awaitable[None]] | None = None,
    ) -> None:
        self._inner = inner
        self._max_retries = max_retries
        self._timeout = timeout_seconds
        self._base_delay = base_delay_seconds
        self._sleep = sleep or asyncio.sleep

    async def complete(self, prompt: str) -> str:
        error: DogmaSystemException = CentralDogmaLockdown("LLM")
        for attempt in range(self._max_retries + 1):
            try:
                return await asyncio.wait_for(self._inner.complete(prompt), timeout=self._timeout)
            except TimeoutError:
                error = CentralDogmaLockdown("LLM (timeout)")
            except (ATFieldInterference, CentralDogmaLockdown) as exc:
                error = exc
            if attempt < self._max_retries:
                await self._sleep(self._base_delay * (2**attempt))
        raise error
