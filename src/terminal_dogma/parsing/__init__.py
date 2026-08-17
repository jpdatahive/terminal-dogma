"""Parser puro das saídas textuais dos agentes."""

from terminal_dogma.parsing.parser import (
    parse_alignment,
    parse_magi_vote,
    parse_potential,
    parse_seele_report,
    parse_veto,
)

__all__ = [
    "parse_alignment",
    "parse_magi_vote",
    "parse_potential",
    "parse_seele_report",
    "parse_veto",
]
