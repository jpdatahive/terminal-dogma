"""Decorator de resiliência: timeout por chamada + retry com backoff."""

from collections.abc import Awaitable, Callable

from terminal_dogma.llm.base import LLMClient


class ResilientLLMClient:
    """Envolve um ``LLMClient`` com timeout e retries exponenciais."""

    def __init__(
        self,
        inner: LLMClient,
        *,
        max_retries: int = 2,
        timeout_seconds: float = 30.0,
        base_delay_seconds: float = 0.5,
        sleep: Callable[[float], Awaitable[None]] | None = None,
    ) -> None:
        raise NotImplementedError

    async def complete(self, prompt: str) -> str:
        raise NotImplementedError
