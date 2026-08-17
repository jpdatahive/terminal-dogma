"""Testes de propriedade (hypothesis) do parser.

Propriedades invariantes que valem para QUALQUER entrada, incluindo texto
arbitrário com surrogates e unicode — o parser nunca pode lançar exceção.
"""

from hypothesis import assume, given
from hypothesis import strategies as st

from terminal_dogma.domain.verdicts import (
    LilithAlignment,
    MagiVote,
    ParadigmPotential,
    VetoStatus,
)
from terminal_dogma.parsing import (
    parse_alignment,
    parse_magi_vote,
    parse_potential,
    parse_seele_report,
    parse_veto,
)

_ANY_TEXT = st.text()
_CLEAN_ANALYSIS = st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=300)


class TestNeverRaises:
    @given(_ANY_TEXT)
    def test_parse_magi_vote(self, text):
        result = parse_magi_vote(text)
        assert isinstance(result.analysis, str)
        assert result.vote is None or isinstance(result.vote, MagiVote)

    @given(_ANY_TEXT)
    def test_parse_seele_report(self, text):
        result = parse_seele_report(text)
        assert isinstance(result.intervention, bool)
        assert isinstance(result.analysis, str)

    @given(_ANY_TEXT)
    def test_parse_potential(self, text):
        result = parse_potential(text)
        assert result.potential is None or isinstance(result.potential, ParadigmPotential)

    @given(_ANY_TEXT)
    def test_parse_alignment(self, text):
        result = parse_alignment(text)
        assert result.alignment is None or isinstance(result.alignment, LilithAlignment)

    @given(_ANY_TEXT)
    def test_parse_veto(self, text):
        result = parse_veto(text)
        assert isinstance(result.status, VetoStatus)
        assert result.raw == text


class TestRoundTrip:
    """Saídas dentro do contrato devem ser recuperadas exatamente."""

    @given(analysis=_CLEAN_ANALYSIS, vote=st.sampled_from(MagiVote))
    def test_magi(self, analysis, vote):
        assume("VOTO" not in analysis.upper())
        result = parse_magi_vote(f"{analysis}\nVOTO: {vote.value}")
        assert result.vote == vote
        assert result.analysis == analysis.strip()

    @given(analysis=_CLEAN_ANALYSIS, potential=st.sampled_from(ParadigmPotential))
    def test_potential(self, analysis, potential):
        assume("POTENCIAL" not in analysis.upper())
        result = parse_potential(f"{analysis}\nPOTENCIAL: {potential.value}")
        assert result.potential == potential
        assert result.analysis == analysis.strip()

    @given(analysis=_CLEAN_ANALYSIS, alignment=st.sampled_from(LilithAlignment))
    def test_alignment(self, analysis, alignment):
        assume("ALINHAMENTO" not in analysis.upper())
        result = parse_alignment(f"{analysis}\nALINHAMENTO: {alignment.value}")
        assert result.alignment == alignment
        assert result.analysis == analysis.strip()

    @given(rule=_CLEAN_ANALYSIS)
    def test_veto_triggered(self, rule):
        assume(rule.strip())
        result = parse_veto(f"VETO ACIONADO: {rule}")
        assert result.status is VetoStatus.VETO_TRIGGERED
        assert result.violated_rule == " ".join(rule.split())

    @given(intervene=st.booleans(), analysis=_CLEAN_ANALYSIS, alert=_CLEAN_ANALYSIS)
    def test_seele(self, intervene, analysis, alert):
        for forbidden in ("INTERVEN", "ANÁLISE", "ANALISE", "ALERTA"):
            assume(forbidden not in analysis.upper())
        assume("ALERTA" not in alert.upper())
        decision = "SIM" if intervene else "NÃO"
        text = f"INTERVENÇÃO: {decision}\nANÁLISE: {analysis}\nALERTA: {alert}"
        result = parse_seele_report(text)
        assert result.intervention is intervene
        assert result.analysis == analysis.strip()
        assert result.alert == (alert.strip() or None)
