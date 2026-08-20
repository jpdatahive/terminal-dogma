"""Serviço de verificação e aplicação de veto da Lança de Longinus."""

from terminal_dogma.agents import LONGINUS, Agent
from terminal_dogma.domain.models import VetoResult
from terminal_dogma.llm.base import LLMClient
from terminal_dogma.state.store import StateStore


class LonginusVetoService:
    """Verifica consultas contra as regras fundamentais e invioláveis do sistema."""

    def __init__(
        self,
        client: LLMClient,
        store: StateStore,
        agent: Agent | None = None,
    ) -> None:
        self._agent = agent or Agent(LONGINUS, client)
        self._store = store

    async def check_veto(self, query: str) -> VetoResult:
        """Avalia a consulta e, em caso de veto acionado, incrementa o contador."""
        result = await self._agent.analyze(query)
        assert isinstance(result, VetoResult)
        if result.vetoed:
            state = self._store.load()
            self._store.save(
                state.model_copy(update={"longinus_activations": state.longinus_activations + 1})
            )
        return result
