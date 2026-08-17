"""Agentes do Terminal Dogma: specs estáticas, catálogo e executor."""

from terminal_dogma.agents.base import Agent
from terminal_dogma.agents.registry import (
    AGENTS_BY_ID,
    ALL_AGENTS,
    MAGI_UNITS,
)
from terminal_dogma.agents.spec import QUERY_PLACEHOLDER, AgentSpec

__all__ = [
    "AGENTS_BY_ID",
    "ALL_AGENTS",
    "MAGI_UNITS",
    "QUERY_PLACEHOLDER",
    "Agent",
    "AgentSpec",
]
