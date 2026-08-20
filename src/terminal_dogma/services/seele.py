"""Serviço de vigilância e análise de risco do comitê SEELE."""

from terminal_dogma.agents import SEELE, Agent
from terminal_dogma.domain.models import SeeleReport
from terminal_dogma.llm.base import LLMClient
from terminal_dogma.state.store import StateStore


class SeeleMonitor:
    """Monitora consultas e comandos para detectar riscos existenciais e desvios de cenário."""

    def __init__(
        self,
        client: LLMClient,
        store: StateStore,
        agent: Agent | None = None,
    ) -> None:
        self._agent = agent or Agent(SEELE, client)
        self._store = store

    async def monitor(self, query: str) -> SeeleReport:
        """Verificação silenciosa de intervenção em background."""
        return await self._analyze(query)

    async def analyze_explicit(self, query: str) -> SeeleReport:
        """Análise de risco solicitada explicitamente pelo usuário."""
        return await self._analyze(query)

    async def _analyze(self, query: str) -> SeeleReport:
        result = await self._agent.analyze(query)
        assert isinstance(result, SeeleReport)
        if result.intervention:
            state = self._store.load()
            self._store.save(
                state.model_copy(update={"seele_interventions": state.seele_interventions + 1})
            )
        return result
