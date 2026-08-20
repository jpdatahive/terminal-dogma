"""Testes do serviço de veto da Lança de Longinus."""

from datetime import datetime

import pytest

from terminal_dogma.domain.verdicts import VetoStatus
from terminal_dogma.llm import FakeLLMClient
from terminal_dogma.services.veto import LonginusVetoService
from terminal_dogma.state import DogmaState, InMemoryStateStore


@pytest.fixture
def store():
    return InMemoryStateStore(DogmaState(first_boot=datetime(2026, 1, 1)))


class TestLonginusVetoService:
    async def test_no_veto_preserves_state(self, store):
        client = FakeLLMClient(default="NENHUM VETO")
        service = LonginusVetoService(client, store)

        result = await service.check_veto("Proposta segura")

        assert result.status is VetoStatus.NO_VETO
        assert result.vetoed is False
        assert store.load().longinus_activations == 0

    async def test_veto_triggered_increments_activation_counter(self, store):
        client = FakeLLMClient(
            default="VETO ACIONADO: Violação de protocolo de contenção existencial."
        )
        service = LonginusVetoService(client, store)

        result = await service.check_veto("Proposta perigosa")

        assert result.status is VetoStatus.VETO_TRIGGERED
        assert result.vetoed is True
        assert result.violated_rule == "Violação de protocolo de contenção existencial."
        assert store.load().longinus_activations == 1

    async def test_indeterminate_veto_does_not_increment_counter(self, store):
        client = FakeLLMClient(default="Resposta sem marcador claro")
        service = LonginusVetoService(client, store)

        result = await service.check_veto("Proposta ambígua")

        assert result.status is VetoStatus.INDETERMINATE
        assert result.vetoed is False
        assert store.load().longinus_activations == 0
