"""Testes do serviço de debate dialético MAGI."""

import pytest

from terminal_dogma.domain.verdicts import MagiVote
from terminal_dogma.llm import FakeLLMClient
from terminal_dogma.services.dialect import DialectService


class TestDialectService:
    async def test_debate_executa_rodadas_com_contexto_cruzado(self):
        responses = {
            "Você é MELCHIOR-01": "Análise Melchior contra-argumentando.\nVOTO: POSITIVO",
            "Você é BALTHASAR-02": (
                "Análise Balthasar considerando impacto humano.\nVOTO: NEGATIVO"
            ),
        }
        client = FakeLLMClient(responses=responses)
        service = DialectService(client)

        debate = await service.debate(
            agent_a_id="melchior-01",
            agent_b_id="balthasar-02",
            query="Devemos automatizar as defesas de Tokyo-3?",
            rounds=2,
        )

        assert debate.query == "Devemos automatizar as defesas de Tokyo-3?"
        assert debate.agent_a_id == "melchior-01"
        assert debate.agent_b_id == "balthasar-02"
        assert len(debate.rounds) == 2
        assert len(client.calls) == 4  # 2 rodadas * 2 agentes

        # Round 1
        r1 = debate.rounds[0]
        assert r1.round_number == 1
        assert r1.agent_a_analysis.vote is MagiVote.POSITIVE
        assert r1.agent_b_analysis.vote is MagiVote.NEGATIVE

        # Contexto do debate deve ser repassado nas chamadas subsequentes
        assert "Contexto do debate" in client.calls[1]  # Agent B na rodada 1
        assert "Contexto do debate" in client.calls[2]  # Agent A na rodada 2

    async def test_mesmo_agente_lanca_erro(self):
        client = FakeLLMClient()
        service = DialectService(client)

        with pytest.raises(ValueError, match="distintos"):
            await service.debate("melchior-01", "melchior-01", "query")

    async def test_agente_invalido_lanca_erro(self):
        client = FakeLLMClient()
        service = DialectService(client)

        with pytest.raises(ValueError, match="inválido"):
            await service.debate("seele", "melchior-01", "query")

    async def test_rodadas_menor_que_um_lanca_erro(self):
        client = FakeLLMClient()
        service = DialectService(client)

        with pytest.raises(ValueError, match="rodadas"):
            await service.debate("melchior-01", "balthasar-02", "query", rounds=0)
