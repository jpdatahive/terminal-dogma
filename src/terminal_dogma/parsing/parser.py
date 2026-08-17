"""Parser puro e tolerante das saídas textuais dos agentes.

Contrato de saída dos prompts v1 (ver ``src/dogma_core/agents.py``):

- MAGI:     ``<análise>\\nVOTO: POSITIVO|NEGATIVO``
- SEELE:    ``INTERVENÇÃO: SIM|NÃO\\nANÁLISE: <texto>\\nALERTA: <frase>``
- ADAM:     ``<análise>\\nPOTENCIAL: DISRUPTIVO|INCREMENTAL``
- LILITH:   ``<análise>\\nALINHAMENTO: ORGÂNICO|FORÇADO``
- LONGINUS: ``NENHUM VETO`` | ``VETO ACIONADO: <regra violada>``

O parser nunca lança exceção: saídas fora do contrato degradam para
veredito ``None`` / ``VetoStatus.INDETERMINATE`` com o texto preservado.
Tolerâncias: caixa alta/baixa, ausência de acentos, marcadores envolvidos
em negrito markdown (``**VOTO: ...**``) e espaços variáveis.
"""

import re
import unicodedata
from collections.abc import Callable, Mapping
from typing import TypeVar

from terminal_dogma.domain.models import (
    AlignmentAssessment,
    AnalysisResult,
    MagiAnalysis,
    PotentialAssessment,
    SeeleReport,
    VetoResult,
)
from terminal_dogma.domain.verdicts import (
    LilithAlignment,
    MagiVote,
    ParadigmPotential,
    VerdictKind,
    VetoStatus,
)

_BOLD = r"(?:\*\*|__)?"
_WS = r"[ \t]*"


def _verdict_re(marker: str, alternatives: str) -> re.Pattern[str]:
    """Monta o regex de um marcador de veredito tolerante a markdown e espaços."""
    return re.compile(
        rf"{_BOLD}{_WS}{marker}{_WS}:{_WS}({alternatives}){_WS}{_BOLD}",
        re.IGNORECASE,
    )


_VOTE_RE = _verdict_re("VOTO", r"POSITIVO|NEGATIVO")
_POTENTIAL_RE = _verdict_re("POTENCIAL", r"DISRUPTIVO|INCREMENTAL")
_ALIGNMENT_RE = _verdict_re("ALINHAMENTO", r"ORG[ÂA]NICO|FOR[ÇC]ADO")

_INTERVENTION_RE = re.compile(rf"INTERVEN[ÇC][ÃA]O{_WS}:{_WS}(SIM|N[ÃA]O)", re.IGNORECASE)
_ANALYSIS_RE = re.compile(
    rf"AN[ÁA]LISE{_WS}:{_WS}(.*?)(?={_WS}{_BOLD}ALERTA{_WS}:|$)",
    re.IGNORECASE | re.DOTALL,
)
_ALERT_RE = re.compile(rf"ALERTA{_WS}:{_WS}(.*)", re.IGNORECASE | re.DOTALL)

_NO_VETO_RE = re.compile(r"NENHUM[ \t]+VETO", re.IGNORECASE)
_VETO_TRIGGERED_RE = re.compile(rf"VETO[ \t]+ACIONADO{_WS}:{_WS}(.*)", re.IGNORECASE | re.DOTALL)

_MAGI_VOTES: Mapping[str, MagiVote] = {
    "POSITIVO": MagiVote.POSITIVE,
    "NEGATIVO": MagiVote.NEGATIVE,
}
_POTENTIALS: Mapping[str, ParadigmPotential] = {
    "DISRUPTIVO": ParadigmPotential.DISRUPTIVE,
    "INCREMENTAL": ParadigmPotential.INCREMENTAL,
}
_ALIGNMENTS: Mapping[str, LilithAlignment] = {
    "ORGANICO": LilithAlignment.ORGANIC,
    "FORCADO": LilithAlignment.FORCED,
}


def _normalize_token(token: str) -> str:
    """Normaliza um token para comparação: maiúsculas e sem acentos."""
    nfkd = unicodedata.normalize("NFKD", token.strip().upper())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


_T = TypeVar("_T")


def _lookup(mapping: Mapping[str, _T], token: str | None) -> _T | None:
    """Busca tolerante de token em um mapa; retorna None se ausente/desconhecido."""
    if token is None:
        return None
    return mapping.get(_normalize_token(token))


def _split_verdict(text: str, pattern: re.Pattern[str]) -> tuple[str, str | None]:
    """Separa a análise do marcador de veredito.

    A última ocorrência do marcador vence (voto final); a análise é o texto
    restante (antes e depois do marcador), com espaços aparados.
    """
    matches = list(pattern.finditer(text))
    if not matches:
        return text.strip(), None
    last = matches[-1]
    analysis = (text[: last.start()] + text[last.end() :]).strip()
    return analysis, last.group(1)


def parse_magi_vote(text: str) -> MagiAnalysis:
    """Extrai análise e voto de uma unidade MAGI."""
    analysis, token = _split_verdict(text, _VOTE_RE)
    return MagiAnalysis(analysis=analysis, vote=_lookup(_MAGI_VOTES, token))


def parse_potential(text: str) -> PotentialAssessment:
    """Extrai análise e veredito de potencial (ADAM)."""
    analysis, token = _split_verdict(text, _POTENTIAL_RE)
    return PotentialAssessment(analysis=analysis, potential=_lookup(_POTENTIALS, token))


def parse_alignment(text: str) -> AlignmentAssessment:
    """Extrai análise e veredito de alinhamento (LILITH)."""
    analysis, token = _split_verdict(text, _ALIGNMENT_RE)
    return AlignmentAssessment(analysis=analysis, alignment=_lookup(_ALIGNMENTS, token))


def parse_seele_report(text: str) -> SeeleReport:
    """Extrai intervenção, análise e alerta de um relatório SEELE.

    Sem o marcador INTERVENÇÃO, o texto integral é tratado como análise e a
    intervenção permanece falsa (relatório não estruturado nunca interrompe
    o fluxo — semântica da v1).
    """
    intervention_match = _INTERVENTION_RE.search(text)
    if intervention_match is None:
        return SeeleReport(intervention=False, analysis=text.strip())

    intervention = _normalize_token(intervention_match.group(1)) == "SIM"

    analysis_match = _ANALYSIS_RE.search(text)
    if analysis_match is not None:
        analysis = analysis_match.group(1).strip()
    else:
        analysis = text[: intervention_match.start()].strip()

    alert_match = _ALERT_RE.search(text)
    alert = alert_match.group(1).strip() if alert_match is not None else ""

    return SeeleReport(intervention=intervention, analysis=analysis, alert=alert or None)


def parse_veto(text: str) -> VetoResult:
    """Interpreta a resposta binária da Lança de Longinus.

    ``VETO ACIONADO`` tem prioridade sobre ``NENHUM VETO`` caso ambos
    apareçam; sem nenhum dos marcadores o status é INDETERMINADO (não
    bloqueia o fluxo, mas fica registrado em ``raw``).
    """
    triggered_match = _VETO_TRIGGERED_RE.search(text)
    if triggered_match is not None:
        rule = " ".join(triggered_match.group(1).split())
        # Desembrulha negrito markdown (``**regra**``) sem tocar em asteriscos
        # que façam parte do próprio texto da regra.
        if rule.startswith("**") and rule.endswith("**") and len(rule) > 4:
            rule = rule[2:-2].strip()
        return VetoResult(status=VetoStatus.VETO_TRIGGERED, violated_rule=rule or None, raw=text)

    if _NO_VETO_RE.search(text) is not None:
        return VetoResult(status=VetoStatus.NO_VETO, raw=text)

    return VetoResult(status=VetoStatus.INDETERMINATE, raw=text)


#: Despacho de tipo de veredito → função de parsing.
PARSERS: Mapping[VerdictKind, Callable[[str], AnalysisResult]] = {
    VerdictKind.MAGI_VOTE: parse_magi_vote,
    VerdictKind.SEELE_REPORT: parse_seele_report,
    VerdictKind.POTENTIAL: parse_potential,
    VerdictKind.ALIGNMENT: parse_alignment,
    VerdictKind.VETO: parse_veto,
}


def parse_output(kind: VerdictKind, text: str) -> AnalysisResult:
    """Faz o parse de ``text`` com o parser do tipo de veredito do agente."""
    return PARSERS[kind](text)
