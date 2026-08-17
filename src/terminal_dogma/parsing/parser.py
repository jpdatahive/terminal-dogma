"""Parser puro e tolerante das saídas textuais dos agentes.

Contrato de saída dos prompts v1 (ver ``src/dogma_core/agents.py``):

- MAGI:     ``<análise>\\nVOTO: POSITIVO|NEGATIVO``
- SEELE:    ``INTERVENÇÃO: SIM|NÃO\\nANÁLISE: <texto>\\nALERTA: <frase>``
- ADAM:     ``<análise>\\nPOTENCIAL: DISRUPTIVO|INCREMENTAL``
- LILITH:   ``<análise>\\nALINHAMENTO: ORGÂNICO|FORÇADO``
- LONGINUS: ``NENHUM VETO`` | ``VETO ACIONADO: <regra violada>``

O parser nunca lança exceção: saídas fora do contrato degradam para
veredito ``None`` / ``VetoStatus.INDETERMINATE`` com o texto preservado.
"""

from terminal_dogma.domain.models import (
    AlignmentAssessment,
    MagiAnalysis,
    PotentialAssessment,
    SeeleReport,
    VetoResult,
)


def parse_magi_vote(text: str) -> MagiAnalysis:
    """Extrai análise e voto de uma unidade MAGI."""
    raise NotImplementedError


def parse_seele_report(text: str) -> SeeleReport:
    """Extrai intervenção, análise e alerta de um relatório SEELE."""
    raise NotImplementedError


def parse_potential(text: str) -> PotentialAssessment:
    """Extrai análise e veredito de potencial (ADAM)."""
    raise NotImplementedError


def parse_alignment(text: str) -> AlignmentAssessment:
    """Extrai análise e veredito de alinhamento (LILITH)."""
    raise NotImplementedError


def parse_veto(text: str) -> VetoResult:
    """Interpreta a resposta binária da Lança de Longinus."""
    raise NotImplementedError
