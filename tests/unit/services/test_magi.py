"""Testes da deliberação do conselho MAGI."""

from datetime import datetime

import pytest

from terminal_dogma.domain.verdicts import MagiVote, VetoStatus
from terminal_dogma.llm import FakeLLMClient
from terminal_dogma.services.magi import MagiCouncil
from terminal_dogma.state import DogmaState, InMemoryStateStore


@pytest.fixture
def store():
    return InMemoryStateStore(DogmaState(first_boot=datetime(2026, 1, 1)))


class TestMagiCouncil:
    async def test_deliberacao_vetada_nao_consulta_magi(self, store):
        responses = {
            "Lança de Longinus": "VETO ACIONADO: Violação grave",
            "MELCHIOR-01": "Análise Melchior.\nVOTO: POSITIVO",
            "BALTHASAR-02": "Análise Balthasar.\nVOTO: POSITIVO",
            "CASPER-03": "Análise Casper.\nVOTO: POSITIVO",
        }
        client = FakeLLMClient(responses=responses)
        council = MagiCouncil(client, store)

        delib = await council.deliberate("Proposta inadmissível")

        assert delib.vetoed is True
        assert delib.veto.status is VetoStatus.VETO_TRIGGERED
        assert delib.analyses == {}
        assert delib.approved is False
        assert len(client.calls) == 1
        assert "Lança de Longinus" in client.calls[0]
        assert store.load().longinus_activations == 1

    async def test_deliberacao_aprovada_por_maioria(self, store):
        responses = {
            "Lança de Longinus": "NENHUM VETO",
            "MELCHIOR-01": "Análise lógica.\nVOTO: POSITIVO",
            "BALTHASAR-02": "Análise ética.\nVOTO: NEGATIVO",
            "CASPER-03": "Análise estratégica.\nVOTO: POSITIVO",
        }
        client = FakeLLMClient(responses=responses)
        council = MagiCouncil(client, store)

        delib = await council.deliberate("Construir nova doca")

        assert delib.vetoed is False
        assert len(delib.analyses) == 3
        assert delib.analyses["melchior-01"].vote is MagiVote.POSITIVE
        assert delib.analyses["balthasar-02"].vote is MagiVote.NEGATIVE
        assert delib.analyses["casper-03"].vote is MagiVote.POSITIVE
        assert delib.positive_votes == 2
        assert delib.negative_votes == 1
        assert delib.approved is True
        assert delib.is_unanimous is False
        assert len(client.calls) == 4  # Longinus + 3 MAGI

    async def test_deliberacao_unanime_rejeitada(self, store):
        responses = {
            "Lança de Longinus": "NENHUM VETO",
            "MELCHIOR-01": "Inviável.\nVOTO: NEGATIVO",
            "BALTHASAR-02": "Antiético.\nVOTO: NEGATIVO",
            "CASPER-03": "Muito arriscado.\nVOTO: NEGATIVO",
        }
        client = FakeLLMClient(responses=responses)
        council = MagiCouncil(client, store)

        delib = await council.deliberate("Proposta ruim")

        assert delib.vetoed is False
        assert delib.positive_votes == 0
        assert delib.negative_votes == 3
        assert delib.approved is False
        assert delib.is_unanimous is True
