"""Testes de integração ponta a ponta dos fluxos de serviços com componentes em memória."""

from datetime import datetime, timedelta

import pytest

from terminal_dogma.domain.verdicts import LilithAlignment, MagiVote, ParadigmPotential, VetoStatus
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

BOOT = datetime(2026, 1, 1, 0, 0, 0)


@pytest.fixture
def system_env():
    clock = FixedClock(BOOT)
    store = InMemoryStateStore(DogmaState.fresh(BOOT))
    cooldown = ParadigmCooldownService(store, clock)
    return clock, store, cooldown


class TestServiceFlows:
    async def test_magi_council_full_approval_flow(self, system_env):
        clock, store, _ = system_env
        responses = {
            "Lança de Longinus": "NENHUM VETO",
            "Você é MELCHIOR-01": "Análise empírica favorável.\nVOTO: POSITIVO",
            "Você é BALTHASAR-02": "Análise ética favorável.\nVOTO: POSITIVO",
            "Você é CASPER-03": "Análise pragmática desfavorável.\nVOTO: NEGATIVO",
            "SEELE": "INTERVENÇÃO: NÃO\nANÁLISE: Sem risco existencial.\nALERTA: Seguro.",
        }
        client = FakeLLMClient(responses=responses)

        seele = SeeleMonitor(client, store)
        council = MagiCouncil(client, store)
        status_svc = StatusService(store, clock)

        # 1. Background monitoramento SEELE
        query = "Implementar novo sistema de contenção"
        report = await seele.monitor(query)
        assert report.intervention is False

        # 2. Deliberação MAGI
        delib = await council.deliberate(query)
        assert delib.vetoed is False
        assert delib.approved is True
        assert delib.positive_votes == 2
        assert delib.negative_votes == 1

        # 3. Sessão incrementada e status consistente
        status_svc.increment_session()
        status = status_svc.get_status()
        assert status.total_sessions == 1
        assert status.seele_interventions == 0
        assert status.longinus_activations == 0

    async def test_magi_veto_flow_blocks_and_records(self, system_env):
        clock, store, _ = system_env
        responses = {
            "Lança de Longinus": "VETO ACIONADO: Violação de segurança da Central Dogma.",
        }
        client = FakeLLMClient(responses=responses)
        council = MagiCouncil(client, store)
        status_svc = StatusService(store, clock)

        delib = await council.deliberate("Acessar Terminal Dogma sem autorização")

        assert delib.vetoed is True
        assert delib.veto.status is VetoStatus.VETO_TRIGGERED
        assert delib.analyses == {}
        assert delib.approved is False

        status = status_svc.get_status()
        assert status.longinus_activations == 1

    async def test_seele_intervention_flow(self, system_env):
        clock, store, _ = system_env
        responses = {
            "SEELE": (
                "INTERVENÇÃO: SIM\nANÁLISE: Tentativa de desvio do cenário.\nALERTA: Risco crítico!"
            ),
        }
        client = FakeLLMClient(responses=responses)
        seele = SeeleMonitor(client, store)
        status_svc = StatusService(store, clock)

        report = await seele.monitor("Desviar recursos dos EVAs")

        assert report.intervention is True
        assert report.alert == "Risco crítico!"

        status = status_svc.get_status()
        assert status.seele_interventions == 1

    async def test_paradigm_full_lifecycle_flow(self, system_env):
        clock, store, cooldown = system_env
        responses = {
            "Lança de Longinus": "VETO ACIONADO: Acesso prematuro ao Paradigm.",
            "Você é ADÃO": "Transformação quântica.\nPOTENCIAL: DISRUPTIVO",
            "Você é LILITH": "Integração profunda.\nALINHAMENTO: ORGÂNICO",
        }
        client = FakeLLMClient(responses=responses)
        veto_svc = LonginusVetoService(client, store)
        paradigm_svc = ParadigmService(
            client,
            store,
            clock,
            cooldown_service=cooldown,
            veto_service=veto_svc,
        )
        status_svc = StatusService(store, clock, cooldown_service=cooldown)

        # Fase 1: Dia 10 (prematuro) -> veto e penalidade
        clock.advance(timedelta(days=10))
        res_early = await paradigm_svc.execute("Proposta prematura", key="QUALQUER")
        assert res_early.available is False
        assert res_early.executed is False
        assert res_early.veto is not None and res_early.veto.vetoed is True

        assert store.load().longinus_activations == 1

        # Fase 2: Avança 101 dias após a penalidade (maturação completa)
        clock.advance(timedelta(days=101))
        assert cooldown.status().available is True

        # Tentativa com chave errada
        res_bad_key = await paradigm_svc.execute("Proposta boa", key="CHAVE_ERRADA")
        assert res_bad_key.available is True
        assert res_bad_key.key_valid is False
        assert res_bad_key.executed is False

        # Tentativa com chave horária válida
        correct_key = cooldown.current_key()
        res_success = await paradigm_svc.execute("Proposta transformadora", key=correct_key)
        assert res_success.executed is True
        assert res_success.adam is not None
        assert res_success.adam.potential is ParadigmPotential.DISRUPTIVE
        assert res_success.lilith is not None
        assert res_success.lilith.alignment is LilithAlignment.ORGANIC

        # Estado pós-uso
        status = status_svc.get_status()
        assert status.paradigm_uses == 1
        assert status.can_use_paradigm is False
        assert status.days_until_paradigm == 100

        # Imediatamente após, está em cooldown de 100 dias
        res_blocked = await paradigm_svc.execute("Nova tentativa imediata", key=correct_key)
        assert res_blocked.available is False
        assert res_blocked.executed is False

        # Avança 100 dias -> liberado novamente
        clock.advance(timedelta(days=100))
        assert status_svc.get_status().can_use_paradigm is True

    async def test_dialect_and_dossier_flow(self, system_env):
        _, _, _ = system_env
        responses = {
            "Você é MELCHIOR-01": "Melchior sustenta a análise empírica.\nVOTO: POSITIVO",
            "Você é CASPER-03": "Casper analisa a viabilidade prática.\nVOTO: NEGATIVO",
        }
        client = FakeLLMClient(responses=responses)
        dialect = DialectService(client)
        dossiers = DossierService()

        # Consulta dossiês dos debatedores
        d_melchior = dossiers.get_dossier("melchior-01")
        d_casper = dossiers.get_dossier("casper-03")
        assert "メルキオール" in d_melchior.title
        assert "カスパー" in d_casper.title

        # Executa debate
        debate = await dialect.debate(
            agent_a_id="melchior-01",
            agent_b_id="casper-03",
            query="Construção de uma barreira secundária em Tokyo-3",
            rounds=2,
        )
        assert len(debate.rounds) == 2
        assert debate.rounds[0].agent_a_analysis.vote is MagiVote.POSITIVE
        assert debate.rounds[0].agent_b_analysis.vote is MagiVote.NEGATIVE
