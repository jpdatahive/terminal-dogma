"""Testes do serviço de monitoramento SEELE."""

from datetime import datetime

import pytest

from terminal_dogma.llm import FakeLLMClient
from terminal_dogma.services.seele import SeeleMonitor
from terminal_dogma.state import DogmaState, InMemoryStateStore


@pytest.fixture
def store():
    return InMemoryStateStore(DogmaState(first_boot=datetime(2026, 1, 1)))


class TestSeeleMonitor:
    async def test_monitor_sem_intervencao_preserva_estado(self, store):
        client = FakeLLMClient(
            default="INTERVENÇÃO: NÃO\nANÁLISE: Sem riscos iminentes.\nALERTA: Seguro."
        )
        monitor = SeeleMonitor(client, store)

        report = await monitor.monitor("Consulta rotineira")

        assert report.intervention is False
        assert report.analysis == "Sem riscos iminentes."
        assert store.load().seele_interventions == 0

    async def test_monitor_com_intervencao_incrementa_contador(self, store):
        client = FakeLLMClient(
            default=(
                "INTERVENÇÃO: SIM\n"
                "ANÁLISE: Risco iminente de desvio do cenário.\n"
                "ALERTA: Alerta vermelho."
            )
        )
        monitor = SeeleMonitor(client, store)

        report = await monitor.monitor("Ativar protocolo proibido")

        assert report.intervention is True
        assert report.analysis == "Risco iminente de desvio do cenário."
        assert report.alert == "Alerta vermelho."
        assert store.load().seele_interventions == 1

    async def test_analyze_explicit_retorna_relatorio(self, store):
        client = FakeLLMClient(
            default=(
                "INTERVENÇÃO: NÃO\n"
                "ANÁLISE: Análise de risco detalhada solicitada.\n"
                "ALERTA: Nenhum risco crítico."
            )
        )
        monitor = SeeleMonitor(client, store)

        report = await monitor.analyze_explicit("Analisar vulnerabilidades da NERV")

        assert report.intervention is False
        assert "Análise de risco detalhada" in report.analysis
        assert store.load().seele_interventions == 0
