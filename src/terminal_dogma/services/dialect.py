"""Serviço de debate dialético entre unidades MAGI."""

from terminal_dogma.agents import AGENTS_BY_ID, MAGI_UNITS, Agent
from terminal_dogma.domain.models import DialectDebate, DialectRound, MagiAnalysis
from terminal_dogma.llm.base import LLMClient

_VALID_MAGI_IDS = {spec.id for spec in MAGI_UNITS}


class DialectService:
    """Coordena debates estruturados em rodadas entre duas unidades MAGI."""

    def __init__(self, client: LLMClient) -> None:
        self._client = client
        self._agents = {spec.id: Agent(spec, client) for spec in MAGI_UNITS}

    async def debate(
        self,
        agent_a_id: str,
        agent_b_id: str,
        query: str,
        rounds: int = 2,
    ) -> DialectDebate:
        """Executa o debate alternando análises e alimentando o contexto do oponente."""
        clean_a = agent_a_id.strip().lower()
        clean_b = agent_b_id.strip().lower()

        if clean_a not in _VALID_MAGI_IDS or clean_b not in _VALID_MAGI_IDS:
            raise ValueError(
                f"ID de agente inválido para dialética. Use: {', '.join(sorted(_VALID_MAGI_IDS))}."
            )

        if clean_a == clean_b:
            raise ValueError("Os agentes devem ser distintos para um debate.")

        if rounds < 1:
            raise ValueError("O número de rodadas deve ser maior ou igual a 1.")

        agent_a = self._agents[clean_a]
        agent_b = self._agents[clean_b]
        spec_a = AGENTS_BY_ID[clean_a]
        spec_b = AGENTS_BY_ID[clean_b]

        rounds_list: list[DialectRound] = []
        last_a_analysis = ""
        last_b_analysis = ""

        for r in range(1, rounds + 1):
            if last_b_analysis:
                context_a = (
                    f"Consulta: {query}\n\n"
                    f"Contexto do debate (última análise de {spec_b.name}): {last_b_analysis}"
                )
            else:
                context_a = query

            res_a = await agent_a.analyze(context_a)
            assert isinstance(res_a, MagiAnalysis)
            last_a_analysis = res_a.analysis

            context_b = (
                f"Consulta: {query}\n\n"
                f"Contexto do debate (última análise de {spec_a.name}): {last_a_analysis}"
            )
            res_b = await agent_b.analyze(context_b)
            assert isinstance(res_b, MagiAnalysis)
            last_b_analysis = res_b.analysis

            rounds_list.append(
                DialectRound(
                    round_number=r,
                    agent_a_analysis=res_a,
                    agent_b_analysis=res_b,
                )
            )

        return DialectDebate(
            query=query,
            agent_a_id=clean_a,
            agent_b_id=clean_b,
            rounds=rounds_list,
        )
