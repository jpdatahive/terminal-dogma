"""Enums de veredito produzidos pelos agentes do Terminal Dogma.

Os *valores* são os tokens em PT-BR do contrato de prompt da v1
(ver ``src/dogma_core/agents.py``); os *nomes* seguem o inglês do código.
"""

from enum import StrEnum


class MagiVote(StrEnum):
    """Voto de uma unidade MAGI (Melchior, Balthasar, Casper)."""

    POSITIVE = "POSITIVO"
    NEGATIVE = "NEGATIVO"


class ParadigmPotential(StrEnum):
    """Veredito de potencial disruptivo emitido por ADAM."""

    DISRUPTIVE = "DISRUPTIVO"
    INCREMENTAL = "INCREMENTAL"


class LilithAlignment(StrEnum):
    """Veredito de alinhamento cultural emitido por LILITH."""

    ORGANIC = "ORGÂNICO"
    FORCED = "FORÇADO"


class VetoStatus(StrEnum):
    """Resultado da verificação da Lança de Longinus."""

    NO_VETO = "NENHUM VETO"
    VETO_TRIGGERED = "VETO ACIONADO"
    INDETERMINATE = "INDETERMINADO"
