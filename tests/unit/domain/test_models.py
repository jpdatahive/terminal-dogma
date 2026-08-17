"""Testes dos modelos de domínio."""

import pytest
from pydantic import ValidationError

from terminal_dogma.domain.models import MagiAnalysis, SeeleReport, VetoResult
from terminal_dogma.domain.verdicts import MagiVote, VetoStatus


def test_modelos_sao_imutaveis():
    analysis = MagiAnalysis(analysis="texto", vote=MagiVote.POSITIVE)
    with pytest.raises(ValidationError):
        analysis.vote = MagiVote.NEGATIVE


def test_veredito_none_representa_indeterminado():
    analysis = MagiAnalysis(analysis="texto sem marcador")
    assert analysis.vote is None


def test_veto_acionado_e_o_unico_status_que_bloqueia():
    triggered = VetoResult(status=VetoStatus.VETO_TRIGGERED, violated_rule="regra X")
    no_veto = VetoResult(status=VetoStatus.NO_VETO)
    indeterminate = VetoResult(status=VetoStatus.INDETERMINATE)

    assert triggered.vetoed is True
    assert no_veto.vetoed is False
    assert indeterminate.vetoed is False


def test_relatorio_seele_tem_defaults_seguros():
    report = SeeleReport()
    assert report.intervention is False
    assert report.analysis == ""
    assert report.alert is None
