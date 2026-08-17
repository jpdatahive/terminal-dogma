"""Estado unificado do Terminal Dogma: modelo, stores, cooldown e migração."""

from terminal_dogma.state.clock import Clock, FixedClock, SystemClock
from terminal_dogma.state.cooldown import CooldownStatus, ParadigmCooldownService
from terminal_dogma.state.migration import migrate_into, migrate_legacy
from terminal_dogma.state.models import DogmaState
from terminal_dogma.state.store import InMemoryStateStore, JsonStateStore, StateStore

__all__ = [
    "Clock",
    "CooldownStatus",
    "DogmaState",
    "FixedClock",
    "InMemoryStateStore",
    "JsonStateStore",
    "ParadigmCooldownService",
    "StateStore",
    "SystemClock",
    "migrate_into",
    "migrate_legacy",
]
