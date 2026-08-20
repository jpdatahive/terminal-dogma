"""Agentes do Terminal Dogma: specs estáticas, catálogo e executor."""

from terminal_dogma.agents.base import Agent
from terminal_dogma.agents.registry import (
    ADAM,
    AGENTS_BY_ID,
    ALL_AGENTS,
    BALTHASAR,
    CASPER,
    LILITH,
    LONGINUS,
    MAGI_UNITS,
    MELCHIOR,
    SEELE,
)
from terminal_dogma.agents.spec import QUERY_PLACEHOLDER, AgentSpec

__all__ = [
    "ADAM",
    "AGENTS_BY_ID",
    "ALL_AGENTS",
    "BALTHASAR",
    "CASPER",
    "LILITH",
    "LONGINUS",
    "MAGI_UNITS",
    "MELCHIOR",
    "QUERY_PLACEHOLDER",
    "SEELE",
    "Agent",
    "AgentSpec",
]
