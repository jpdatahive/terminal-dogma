"""Testes dos enums de veredito: valores devem casar com o contrato de prompt v1."""

from terminal_dogma.domain.verdicts import (
    LilithAlignment,
    MagiVote,
    ParadigmPotential,
    VetoStatus,
)


def test_voto_magi_casa_tokens_do_contrato():
    assert MagiVote.POSITIVE == "POSITIVO"
    assert MagiVote.NEGATIVE == "NEGATIVO"


def test_potencial_paradigm_casa_tokens_do_contrato():
    assert ParadigmPotential.DISRUPTIVE == "DISRUPTIVO"
    assert ParadigmPotential.INCREMENTAL == "INCREMENTAL"


def test_alinhamento_lilith_casa_tokens_do_contrato():
    assert LilithAlignment.ORGANIC == "ORGÂNICO"
    assert LilithAlignment.FORCED == "FORÇADO"


def test_status_veto_casa_tokens_do_contrato():
    assert VetoStatus.NO_VETO == "NENHUM VETO"
    assert VetoStatus.VETO_TRIGGERED == "VETO ACIONADO"
    assert VetoStatus.INDETERMINATE == "INDETERMINADO"
