"""Modelos de resultado das análises dos agentes (saída tipada do parser).

Todos os modelos são imutáveis (``frozen=True``). Um veredito ``None``
representa o INDETERMINADO da v1: o LLM saiu do contrato e o parser
preservou o texto bruto em ``analysis``.
"""

from pydantic import BaseModel, ConfigDict

from terminal_dogma.domain.verdicts import (
    LilithAlignment,
    MagiVote,
    ParadigmPotential,
    VetoStatus,
)


class MagiAnalysis(BaseModel):
    """Análise de uma unidade MAGI com voto opcional."""

    model_config = ConfigDict(frozen=True)

    analysis: str
    vote: MagiVote | None = None


class SeeleReport(BaseModel):
    """Relatório de risco do comitê SEELE (monitoramento ou análise explícita)."""

    model_config = ConfigDict(frozen=True)

    intervention: bool = False
    analysis: str = ""
    alert: str | None = None


class PotentialAssessment(BaseModel):
    """Avaliação de potencial disruptivo (ADAM)."""

    model_config = ConfigDict(frozen=True)

    analysis: str
    potential: ParadigmPotential | None = None


class AlignmentAssessment(BaseModel):
    """Avaliação de alinhamento cultural (LILITH)."""

    model_config = ConfigDict(frozen=True)

    analysis: str
    alignment: LilithAlignment | None = None


class VetoResult(BaseModel):
    """Resultado da verificação de veto da Lança de Longinus."""

    model_config = ConfigDict(frozen=True)

    status: VetoStatus
    violated_rule: str | None = None
    raw: str = ""

    @property
    def vetoed(self) -> bool:
        """Verdadeiro apenas quando o veto foi explicitamente acionado.

        Saídas INDETERMINADO não bloqueiam o fluxo (semântica da v1).
        """
        return self.status is VetoStatus.VETO_TRIGGERED
