"""Parser puro das saídas textuais dos agentes."""

from terminal_dogma.parsing.parser import (
    PARSERS,
    parse_alignment,
    parse_magi_vote,
    parse_output,
    parse_potential,
    parse_seele_report,
    parse_veto,
)

__all__ = [
    "PARSERS",
    "parse_alignment",
    "parse_magi_vote",
    "parse_output",
    "parse_potential",
    "parse_seele_report",
    "parse_veto",
]
