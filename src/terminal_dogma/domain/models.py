"""Modelos de resultado das análises dos agentes (saída tipada do parser).

Todos os modelos são imutáveis (``frozen=True``). Um veredito ``None``
representa o INDETERMINADO da v1: o LLM saiu do contrato e o parser
preservou o texto bruto em ``analysis``.
"""

from pydantic import BaseModel, ConfigDict, Field

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


class MagiDeliberation(BaseModel):
    """Resultado da deliberação do conselho MAGI (com checagem prévia de veto)."""

    model_config = ConfigDict(frozen=True)

    query: str
    veto: VetoResult
    analyses: dict[str, MagiAnalysis] = Field(default_factory=dict)

    @property
    def vetoed(self) -> bool:
        """Verdadeiro se a deliberação foi cancelada por veto de Longinus."""
        return self.veto.vetoed

    @property
    def positive_votes(self) -> int:
        """Quantidade de votos positivos emitidos pelas unidades MAGI."""
        return sum(1 for a in self.analyses.values() if a.vote is MagiVote.POSITIVE)

    @property
    def negative_votes(self) -> int:
        """Quantidade de votos negativos emitidos pelas unidades MAGI."""
        return sum(1 for a in self.analyses.values() if a.vote is MagiVote.NEGATIVE)

    @property
    def indeterminate_votes(self) -> int:
        """Quantidade de votos indeterminados (saída fora de contrato)."""
        return sum(1 for a in self.analyses.values() if a.vote is None)

    @property
    def approved(self) -> bool:
        """Aprovado por maioria simples das unidades votantes se não vetado."""
        if self.vetoed or not self.analyses:
            return False
        return self.positive_votes > self.negative_votes

    @property
    def is_unanimous(self) -> bool:
        """Unânime se todos os votantes concordaram (todos positivos ou todos negativos)."""
        if not self.analyses:
            return False
        total = len(self.analyses)
        return self.positive_votes == total or self.negative_votes == total


class ParadigmExecution(BaseModel):
    """Resultado da execução do sistema Progenitor (ADAM + LILITH)."""

    model_config = ConfigDict(frozen=True)

    query: str
    available: bool
    cooldown_reason: str = ""
    key_valid: bool = True
    veto: VetoResult | None = None
    adam: PotentialAssessment | None = None
    lilith: AlignmentAssessment | None = None

    @property
    def executed(self) -> bool:
        """Verdadeiro se a análise conjunta de Adam e Lilith foi executada com sucesso."""
        return (
            self.available and self.key_valid and self.adam is not None and self.lilith is not None
        )


class DialectRound(BaseModel):
    """Uma rodada de debate entre duas unidades MAGI."""

    model_config = ConfigDict(frozen=True)

    round_number: int
    agent_a_analysis: MagiAnalysis
    agent_b_analysis: MagiAnalysis


class DialectDebate(BaseModel):
    """Resultado do debate dialético entre duas unidades MAGI."""

    model_config = ConfigDict(frozen=True)

    query: str
    agent_a_id: str
    agent_b_id: str
    rounds: list[DialectRound] = Field(default_factory=list)


class SystemStatus(BaseModel):
    """Fotografia consolidada do status do sistema para exibição."""

    model_config = ConfigDict(frozen=True)

    days_since_boot: int
    can_use_paradigm: bool
    days_until_paradigm: int
    paradigm_key: str
    paradigm_uses: int
    seele_interventions: int
    longinus_activations: int
    total_sessions: int


class AgentDossier(BaseModel):
    """Dossiê descritivo e temático de um agente."""

    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    title: str
    color: str
    description: str
    activation_date: str
    core_directive: str


#: União de todos os resultados possíveis da análise individual de um agente.
AnalysisResult = MagiAnalysis | SeeleReport | PotentialAssessment | AlignmentAssessment | VetoResult
