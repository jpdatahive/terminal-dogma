"""Testes unitários de renderização dos widgets da TUI."""

from datetime import datetime, timedelta

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
from terminal_dogma.services.status import StatusService
from terminal_dogma.state import DogmaState, FixedClock, InMemoryStateStore
from terminal_dogma.tui.widgets import (
    DialectWidget,
    DossierWidget,
    ErrorWidget,
    HeaderWidget,
    HelpWidget,
    MagiDeliberationWidget,
    ParadigmWidget,
    SeeleWidget,
    StatusBar,
    StatusWidget,
    VetoWidget,
)

BOOT = datetime(2026, 1, 1, 10, 0, 0)


def test_header_widget_render():
    widget = HeaderWidget()
    renderable = widget.render()
    assert renderable is not None


def test_status_bar_render():
    store = InMemoryStateStore(DogmaState(first_boot=BOOT))
    clock = FixedClock(BOOT + timedelta(days=120))
    status_svc = StatusService(store, clock)

    widget = StatusBar(status_svc)
    renderable = widget.render()
    assert renderable is not None

    # Test when in cooldown
    clock_early = FixedClock(BOOT + timedelta(days=10))
    status_svc_early = StatusService(store, clock_early)
    widget_early = StatusBar(status_svc_early)
    assert widget_early.render() is not None


def test_help_widget_render():
    widget = HelpWidget()
    assert widget.render() is not None


def test_status_widget_render():
    status = SystemStatus(
        days_since_boot=150,
        can_use_paradigm=True,
        days_until_paradigm=0,
        paradigm_key="A1B2C3D4",
        paradigm_uses=2,
        seele_interventions=3,
        longinus_activations=1,
        total_sessions=20,
    )
    widget = StatusWidget(status)
    assert widget.render() is not None


def test_dossier_widget_render():
    dossier = AgentDossier(
        id="melchior-01",
        name="MELCHIOR-01",
        title="O Primeiro Sábio",
        color="bold blue",
        description="Lógica empírica.",
        activation_date="2042-08-15",
        core_directive="Observar e prever.",
    )
    widget = DossierWidget(dossier)
    assert widget.render() is not None


def test_veto_widget_render():
    veto_ok = VetoResult(status=VetoStatus.NO_VETO)
    widget_ok = VetoWidget(veto_ok)
    assert widget_ok.render() is not None

    veto_triggered = VetoResult(
        status=VetoStatus.VETO_TRIGGERED, violated_rule="Regra de contenção"
    )
    widget_triggered = VetoWidget(veto_triggered)
    assert widget_triggered.render() is not None


def test_seele_widget_render():
    report_normal = SeeleReport(intervention=False, analysis="Risco moderado", alert="Atenção")
    widget_normal = SeeleWidget(report_normal)
    assert widget_normal.render() is not None

    report_intervention = SeeleReport(
        intervention=True, analysis="Desvio crítico", alert="Alerta vermelho"
    )
    widget_intervention = SeeleWidget(report_intervention, is_intervention=True)
    assert widget_intervention.render() is not None


def test_magi_deliberation_widget_render():
    delib_vetoed = MagiDeliberation(
        query="Ativar algo",
        veto=VetoResult(status=VetoStatus.VETO_TRIGGERED, violated_rule="Violação"),
    )
    widget_vetoed = MagiDeliberationWidget(delib_vetoed)
    assert widget_vetoed.render() is not None

    delib_approved = MagiDeliberation(
        query="Aprovar algo",
        veto=VetoResult(status=VetoStatus.NO_VETO),
        analyses={
            "melchior-01": MagiAnalysis(analysis="Sim", vote=MagiVote.POSITIVE),
            "balthasar-02": MagiAnalysis(analysis="Sim", vote=MagiVote.POSITIVE),
            "casper-03": MagiAnalysis(analysis="Não", vote=MagiVote.NEGATIVE),
        },
    )
    widget_approved = MagiDeliberationWidget(delib_approved)
    assert widget_approved.render() is not None

    delib_rejected_unanimous = MagiDeliberation(
        query="Rejeitar algo",
        veto=VetoResult(status=VetoStatus.NO_VETO),
        analyses={
            "melchior-01": MagiAnalysis(analysis="Não", vote=MagiVote.NEGATIVE),
            "balthasar-02": MagiAnalysis(analysis="Não", vote=MagiVote.NEGATIVE),
            "casper-03": MagiAnalysis(analysis="Não", vote=MagiVote.NEGATIVE),
        },
    )
    widget_rejected = MagiDeliberationWidget(delib_rejected_unanimous)
    assert widget_rejected.render() is not None


def test_paradigm_widget_render():
    res_unavailable = ParadigmExecution(
        query="Query 1",
        available=False,
        cooldown_reason="Em resfriamento",
    )
    widget_unavail = ParadigmWidget(res_unavailable)
    assert widget_unavail.render() is not None

    res_bad_key = ParadigmExecution(
        query="Query 2",
        available=True,
        key_valid=False,
        cooldown_reason="Chave errada",
    )
    widget_bad_key = ParadigmWidget(res_bad_key)
    assert widget_bad_key.render() is not None

    res_success = ParadigmExecution(
        query="Query 3",
        available=True,
        key_valid=True,
        adam=PotentialAssessment(analysis="Disruptivo", potential=ParadigmPotential.DISRUPTIVE),
        lilith=AlignmentAssessment(analysis="Orgânico", alignment=LilithAlignment.ORGANIC),
    )
    widget_success = ParadigmWidget(res_success)
    assert widget_success.render() is not None


def test_dialect_widget_render():
    round1 = DialectRound(
        round_number=1,
        agent_a_analysis=MagiAnalysis(analysis="Análise A", vote=MagiVote.POSITIVE),
        agent_b_analysis=MagiAnalysis(analysis="Análise B", vote=MagiVote.NEGATIVE),
    )
    debate = DialectDebate(
        query="Debate",
        agent_a_id="melchior-01",
        agent_b_id="balthasar-02",
        rounds=[round1],
    )
    widget = DialectWidget(debate)
    assert widget.render() is not None


def test_error_widget_render():
    widget = ErrorWidget("Mensagem de erro de teste")
    assert widget.render() is not None
