"""Testes do serviço de simulação Progenitora (Paradigm: ADAM vs. LILITH)."""

from datetime import datetime, timedelta

import pytest

from terminal_dogma.domain.verdicts import LilithAlignment, ParadigmPotential, VetoStatus
from terminal_dogma.llm import FakeLLMClient
from terminal_dogma.services.paradigm import ParadigmService
from terminal_dogma.state import DogmaState, FixedClock, InMemoryStateStore, ParadigmCooldownService

BOOT = datetime(2026, 1, 1, 12, 0, 0)


@pytest.fixture
def base_setup():
    store = InMemoryStateStore(DogmaState(first_boot=BOOT))
    clock = FixedClock(BOOT + timedelta(days=101))  # maturado
    cooldown = ParadigmCooldownService(store, clock)
    return store, clock, cooldown


class TestParadigmService:
    async def test_execucao_com_sucesso(self, base_setup):
        store, clock, cooldown = base_setup
        key = cooldown.current_key()
        responses = {
            "Você é ADÃO": "Inovação total.\nPOTENCIAL: DISRUPTIVO",
            "Você é LILITH": "Impacto orgânico.\nALINHAMENTO: ORGÂNICO",
        }
        client = FakeLLMClient(responses=responses)
        service = ParadigmService(client, store, clock, cooldown_service=cooldown)

        result = await service.execute("Criar nova tecnologia de energia", key=key)

        assert result.executed is True
        assert result.available is True
        assert result.key_valid is True
        assert result.adam is not None
        assert result.adam.potential is ParadigmPotential.DISRUPTIVE
        assert result.lilith is not None
        assert result.lilith.alignment is LilithAlignment.ORGANIC

        state = store.load()
        assert state.paradigm_uses == 1
        assert state.last_paradigm_use == clock.now()
        # Após uso, entra em cooldown
        assert cooldown.status().available is False

    async def test_tentativa_durante_cooldown_aplica_penalidade_e_aciona_veto(self):
        store = InMemoryStateStore(DogmaState(first_boot=BOOT))
        clock = FixedClock(BOOT + timedelta(days=50))  # não maturado (50 dias)
        cooldown = ParadigmCooldownService(store, clock)
        key = cooldown.current_key()

        responses = {
            "Lança de Longinus": "VETO ACIONADO: Violação de protocolo temporal.",
        }
        client = FakeLLMClient(responses=responses)
        service = ParadigmService(client, store, clock, cooldown_service=cooldown)

        result = await service.execute("Tentativa prematura", key=key)

        assert result.executed is False
        assert result.available is False
        assert "maturação" in result.cooldown_reason
        assert result.veto is not None
        assert result.veto.status is VetoStatus.VETO_TRIGGERED
        assert result.adam is None
        assert result.lilith is None

        # Penalidade aplicada (last_paradigm_use atualizado para now)
        # e ativação de Longinus registrada.
        state = store.load()
        assert state.last_paradigm_use == clock.now()
        assert state.longinus_activations == 1
        assert state.paradigm_uses == 0

    async def test_chave_incorreta_rejeita_sem_penalidade(self, base_setup):
        store, clock, cooldown = base_setup
        client = FakeLLMClient(default="não deve ser chamado")
        service = ParadigmService(client, store, clock, cooldown_service=cooldown)

        result = await service.execute("Consulta válida", key="CHAVE_ERRADA")

        assert result.executed is False
        assert result.available is True
        assert result.key_valid is False
        assert result.adam is None
        assert result.lilith is None
        assert len(client.calls) == 0

        state = store.load()
        assert state.last_paradigm_use is None
        assert state.paradigm_uses == 0
        assert state.longinus_activations == 0
