"""Orquestrador da deliberação do conselho MAGI."""

import asyncio

from terminal_dogma.agents import MAGI_UNITS, Agent
from terminal_dogma.domain.models import MagiAnalysis, MagiDeliberation
from terminal_dogma.llm.base import LLMClient
from terminal_dogma.services.veto import LonginusVetoService
from terminal_dogma.state.store import StateStore


class MagiCouncil:
    """Orquestra a deliberação tripartite MAGI com checagem prévia de veto."""

    def __init__(
        self,
        client: LLMClient,
        store: StateStore,
        veto_service: LonginusVetoService | None = None,
    ) -> None:
        self._veto_service = veto_service or LonginusVetoService(client, store)
        self._units = {spec.id: Agent(spec, client) for spec in MAGI_UNITS}

    async def deliberate(self, query: str) -> MagiDeliberation:
        """Executa a deliberação: primeiro verifica veto; se livre, consulta em paralelo."""
        veto_result = await self._veto_service.check_veto(query)
        if veto_result.vetoed:
            return MagiDeliberation(query=query, veto=veto_result, analyses={})

        tasks = [self._units[spec.id].analyze(query) for spec in MAGI_UNITS]
        results = await asyncio.gather(*tasks)

        analyses: dict[str, MagiAnalysis] = {}
        for spec, res in zip(MAGI_UNITS, results, strict=True):
            assert isinstance(res, MagiAnalysis)
            analyses[spec.id] = res

        return MagiDeliberation(query=query, veto=veto_result, analyses=analyses)
