"""Testes dos modelos de domínio."""

import pytest
from pydantic import ValidationError

from terminal_dogma.domain.models import (
    AgentDossier,
    AlignmentAssessment,
    DialectDebate,
    DialectRound,
    MagiAnalysis,
    MagiDeliberation,
    ParadigmExecution,
    PotentialAssessment,
    SeeleReport,
    SystemStatus,
    VetoResult,
)
from terminal_dogma.domain.verdicts import (
    LilithAlignment,
    MagiVote,
    ParadigmPotential,
    VetoStatus,
)


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


def test_magi_deliberation_properties():
    veto_ok = VetoResult(status=VetoStatus.NO_VETO)
    delib = MagiDeliberation(
        query="Teste de proposta",
        veto=veto_ok,
        analyses={
            "melchior-01": MagiAnalysis(analysis="Ok", vote=MagiVote.POSITIVE),
            "balthasar-02": MagiAnalysis(analysis="Ok", vote=MagiVote.POSITIVE),
            "casper-03": MagiAnalysis(analysis="Não", vote=MagiVote.NEGATIVE),
        },
    )

    assert delib.vetoed is False
    assert delib.positive_votes == 2
    assert delib.negative_votes == 1
    assert delib.indeterminate_votes == 0
    assert delib.approved is True
    assert delib.is_unanimous is False


def test_magi_deliberation_unanimous_and_veto():
    veto_blocked = VetoResult(status=VetoStatus.VETO_TRIGGERED, violated_rule="Regra 1")
    delib_vetoed = MagiDeliberation(
        query="Ataque",
        veto=veto_blocked,
        analyses={},
    )
    assert delib_vetoed.vetoed is True
    assert delib_vetoed.approved is False
    assert delib_vetoed.is_unanimous is False

    veto_ok = VetoResult(status=VetoStatus.NO_VETO)
    delib_unanimous = MagiDeliberation(
        query="Proposta unânime",
        veto=veto_ok,
        analyses={
            "melchior-01": MagiAnalysis(analysis="Sim", vote=MagiVote.POSITIVE),
            "balthasar-02": MagiAnalysis(analysis="Sim", vote=MagiVote.POSITIVE),
            "casper-03": MagiAnalysis(analysis="Sim", vote=MagiVote.POSITIVE),
        },
    )
    assert delib_unanimous.approved is True
    assert delib_unanimous.is_unanimous is True


def test_paradigm_execution_properties():
    exec_ok = ParadigmExecution(
        query="Inovação",
        available=True,
        key_valid=True,
        adam=PotentialAssessment(analysis="Disruptivo", potential=ParadigmPotential.DISRUPTIVE),
        lilith=AlignmentAssessment(analysis="Orgânico", alignment=LilithAlignment.ORGANIC),
    )
    assert exec_ok.executed is True

    exec_cooldown = ParadigmExecution(
        query="Inovação",
        available=False,
        cooldown_reason="Em resfriamento",
        veto=VetoResult(status=VetoStatus.VETO_TRIGGERED),
    )
    assert exec_cooldown.executed is False

    exec_bad_key = ParadigmExecution(
        query="Inovação",
        available=True,
        key_valid=False,
        cooldown_reason="Chave inválida",
    )
    assert exec_bad_key.executed is False


def test_dialect_debate_model():
    round1 = DialectRound(
        round_number=1,
        agent_a_analysis=MagiAnalysis(analysis="A1", vote=MagiVote.POSITIVE),
        agent_b_analysis=MagiAnalysis(analysis="B1", vote=MagiVote.NEGATIVE),
    )
    debate = DialectDebate(
        query="Debate x",
        agent_a_id="melchior-01",
        agent_b_id="balthasar-02",
        rounds=[round1],
    )
    assert debate.query == "Debate x"
    assert len(debate.rounds) == 1
    assert debate.rounds[0].round_number == 1


def test_system_status_and_agent_dossier_models():
    status = SystemStatus(
        days_since_boot=105,
        can_use_paradigm=True,
        days_until_paradigm=0,
        paradigm_key="A1B2C3D4",
        paradigm_uses=1,
        seele_interventions=2,
        longinus_activations=0,
        total_sessions=10,
    )
    assert status.days_since_boot == 105
    assert status.can_use_paradigm is True

    dossier = AgentDossier(
        id="melchior-01",
        name="MELCHIOR-01",
        title="O Primeiro Sábio",
        color="bold blue",
        description="Lógica pura",
        activation_date="2042-08-15",
        core_directive="Observar e prever",
    )
    assert dossier.id == "melchior-01"
