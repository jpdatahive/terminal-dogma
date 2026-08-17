"""Relógios injetáveis: toda regra temporal recebe um ``Clock``."""

from datetime import datetime, timedelta
from typing import Protocol


class Clock(Protocol):
    """Fonte de tempo do sistema."""

    def now(self) -> datetime:
        """Retorna o instante atual."""
        ...


class SystemClock:
    """Relógio real, baseado em ``datetime.now``."""

    def now(self) -> datetime:
        return datetime.now()


class FixedClock:
    """Relógio controlado para testes: só avança via ``advance``."""

    def __init__(self, start: datetime) -> None:
        self._current = start

    def now(self) -> datetime:
        return self._current

    def advance(self, delta: timedelta) -> None:
        self._current += delta
