"""Testes de interface de usuário (TUI) com Textual Pilot."""

from datetime import datetime, timedelta

import pytest
from textual.widgets import Input

from terminal_dogma.llm import FakeLLMClient
from terminal_dogma.services import (
    DialectService,
    DossierService,
    LonginusVetoService,
    MagiCouncil,
    ParadigmService,
    SeeleMonitor,
    StatusService,
)
from terminal_dogma.state import DogmaState, FixedClock, InMemoryStateStore, ParadigmCooldownService
from terminal_dogma.tui.app import DogmaApp
from terminal_dogma.tui.widgets import (
    DialectWidget,
    DossierWidget,
    ErrorWidget,
    HelpWidget,
    MagiDeliberationWidget,
    ParadigmWidget,
    SeeleWidget,
    StatusBar,
    StatusWidget,
    VetoWidget,
)

BOOT = datetime(2026, 1, 1, 12, 0, 0)


@pytest.fixture
def test_app():
    clock = FixedClock(BOOT + timedelta(days=120))  # maturado
    store = InMemoryStateStore(DogmaState.fresh(BOOT))
    cooldown = ParadigmCooldownService(store, clock)

    responses = {
        "Lança de Longinus": "NENHUM VETO",
        "Você é MELCHIOR-01": "Melchior aprovou.\nVOTO: POSITIVO",
        "Você é BALTHASAR-02": "Balthasar aprovou.\nVOTO: POSITIVO",
        "Você é CASPER-03": "Casper rejeitou.\nVOTO: NEGATIVO",
        "SEELE": "INTERVENÇÃO: NÃO\nANÁLISE: Risco aceitável.\nALERTA: Seguro.",
        "Você é ADÃO": "Disrupção total.\nPOTENCIAL: DISRUPTIVO",
        "Você é LILITH": "Harmonia social.\nALINHAMENTO: ORGÂNICO",
    }
    client = FakeLLMClient(responses=responses)

    veto_svc = LonginusVetoService(client, store)
    magi_council = MagiCouncil(client, store, veto_service=veto_svc)
    seele_monitor = SeeleMonitor(client, store)
    paradigm_svc = ParadigmService(
        client, store, clock, cooldown_service=cooldown, veto_service=veto_svc
    )
    dialect_svc = DialectService(client)
    status_svc = StatusService(store, clock, cooldown_service=cooldown)
    dossier_svc = DossierService()

    return DogmaApp(
        council=magi_council,
        seele=seele_monitor,
        paradigm=paradigm_svc,
        veto=veto_svc,
        dialect=dialect_svc,
        status_svc=status_svc,
        dossier_svc=dossier_svc,
        client=client,
        store=store,
        clock=clock,
        cooldown=cooldown,
    )


class TestDogmaApp:
    async def test_app_startup_components(self, test_app):
        async with test_app.run_test() as pilot:
            assert pilot.app.query_one(StatusBar) is not None
            assert pilot.app.query_one(Input) is not None

    async def test_help_command(self, test_app):
        async with test_app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            input_widget.value = "help"
            await pilot.press("enter")
            await pilot.pause()

            help_widgets = pilot.app.query(HelpWidget)
            assert len(help_widgets) == 1

    async def test_status_command(self, test_app):
        async with test_app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            input_widget.value = "status"
            await pilot.press("enter")
            await pilot.pause()

            status_widgets = pilot.app.query(StatusWidget)
            assert len(status_widgets) == 1

    async def test_dossier_command(self, test_app):
        async with test_app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            input_widget.value = "dossier melchior-01"
            await pilot.press("enter")
            await pilot.pause()

            dossier_widgets = pilot.app.query(DossierWidget)
            assert len(dossier_widgets) == 1
            assert dossier_widgets.first().dossier.id == "melchior-01"

    async def test_dossier_unknown_agent(self, test_app):
        async with test_app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            input_widget.value = "dossier desconhecido"
            await pilot.press("enter")
            await pilot.pause()

            error_widgets = pilot.app.query(ErrorWidget)
            assert len(error_widgets) == 1

    async def test_magi_deliberation_command(self, test_app):
        async with test_app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            input_widget.value = "magi Aprovar orçamento de Tóquio-3"
            await pilot.press("enter")
            await pilot.pause()

            magi_widgets = pilot.app.query(MagiDeliberationWidget)
            assert len(magi_widgets) == 1
            delib = magi_widgets.first().deliberation
            assert delib.approved is True
            assert delib.positive_votes == 2

    async def test_seele_command(self, test_app):
        async with test_app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            input_widget.value = "seele Investigar rotas de abastecimento"
            await pilot.press("enter")
            await pilot.pause()

            seele_widgets = pilot.app.query(SeeleWidget)
            assert len(seele_widgets) == 1
            assert seele_widgets.first().report.intervention is False

    async def test_veto_command(self, test_app):
        async with test_app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            input_widget.value = "veto Inspeção geral"
            await pilot.press("enter")
            await pilot.pause()

            veto_widgets = pilot.app.query(VetoWidget)
            assert len(veto_widgets) == 1
            assert veto_widgets.first().result.vetoed is False

    async def test_paradigm_command(self, test_app):
        async with test_app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            input_widget.value = "paradigm Proposta evolutiva"
            await pilot.press("enter")
            await pilot.pause()

            paradigm_widgets = pilot.app.query(ParadigmWidget)
            assert len(paradigm_widgets) == 1
            assert paradigm_widgets.first().result.executed is True

    async def test_dialect_command(self, test_app):
        async with test_app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            input_widget.value = "dialect melchior-01 casper-03 Defesas perimetrais"
            await pilot.press("enter")
            await pilot.pause()

            dialect_widgets = pilot.app.query(DialectWidget)
            assert len(dialect_widgets) == 1
            debate = dialect_widgets.first().debate
            assert len(debate.rounds) == 2

    async def test_clear_command(self, test_app):
        async with test_app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            input_widget.value = "help"
            await pilot.press("enter")
            await pilot.pause()
            assert len(pilot.app.query(HelpWidget)) == 1

            input_widget.value = "clear"
            await pilot.press("enter")
            await pilot.pause()
            assert len(pilot.app.query(HelpWidget)) == 0

    async def test_unknown_command(self, test_app):
        async with test_app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            input_widget.value = "comando_invalido"
            await pilot.press("enter")
            await pilot.pause()

            error_widgets = pilot.app.query(ErrorWidget)
            assert len(error_widgets) == 1

    async def test_empty_input_ignored(self, test_app):
        async with test_app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            input_widget.value = "   "
            await pilot.press("enter")
            await pilot.pause()

            error_widgets = pilot.app.query(ErrorWidget)
            assert len(error_widgets) == 0

    @pytest.mark.parametrize(
        "cmd",
        [
            "magi",
            "seele",
            "veto",
            "paradigm",
            "dossier",
            "dialect",
            "dialect melchior-01",
        ],
    )
    async def test_empty_args_shows_error(self, test_app, cmd):
        async with test_app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            input_widget.value = cmd
            await pilot.press("enter")
            await pilot.pause()

            error_widgets = pilot.app.query(ErrorWidget)
            assert len(error_widgets) == 1

    async def test_magi_with_seele_intervention_displays_both(self):
        responses = {
            "SEELE": ("INTERVENÇÃO: SIM\nANÁLISE: Risco grave detectado.\nALERTA: Alerta SEELE"),
            "Lança de Longinus": "NENHUM VETO",
            "Você é MELCHIOR-01": "Ok.\nVOTO: POSITIVO",
            "Você é BALTHASAR-02": "Ok.\nVOTO: POSITIVO",
            "Você é CASPER-03": "Ok.\nVOTO: POSITIVO",
        }
        client = FakeLLMClient(responses=responses)
        store = InMemoryStateStore(DogmaState(first_boot=BOOT))
        clock = FixedClock(BOOT + timedelta(days=120))
        app = DogmaApp(client=client, store=store, clock=clock)

        async with app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            input_widget.value = "magi Consulta com intervencao"
            await pilot.press("enter")
            await pilot.pause()

            assert len(pilot.app.query(SeeleWidget)) == 1
            assert len(pilot.app.query(MagiDeliberationWidget)) == 1

    async def test_exit_command(self, test_app):
        async with test_app.run_test() as pilot:
            input_widget = pilot.app.query_one(Input)
            input_widget.value = "exit"
            await pilot.press("enter")
            await pilot.pause()
            assert pilot.app.is_running is False


def test_default_factories(monkeypatch, tmp_path):
    from terminal_dogma.tui.app import _default_client, _default_store

    # Sem chave
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    client_fake = _default_client()
    assert isinstance(client_fake, FakeLLMClient)

    # Com chave
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    client_gemini = _default_client()
    assert client_gemini is not None

    # Default store
    monkeypatch.setenv("HOME", str(tmp_path))
    store = _default_store()
    assert store is not None
