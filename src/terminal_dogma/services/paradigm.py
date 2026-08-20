"""Serviço de simulação Progenitora (Paradigm: ADAM vs. LILITH)."""

import asyncio

from terminal_dogma.agents import ADAM, LILITH, Agent
from terminal_dogma.domain.models import AlignmentAssessment, ParadigmExecution, PotentialAssessment
from terminal_dogma.llm.base import LLMClient
from terminal_dogma.services.veto import LonginusVetoService
from terminal_dogma.state.clock import Clock
from terminal_dogma.state.cooldown import ParadigmCooldownService
from terminal_dogma.state.store import StateStore


class ParadigmService:
    """Executa a análise de paradigmas com travas de maturação, cooldown e chave horária."""

    def __init__(
        self,
        client: LLMClient,
        store: StateStore,
        clock: Clock,
        cooldown_service: ParadigmCooldownService | None = None,
        veto_service: LonginusVetoService | None = None,
    ) -> None:
        self._cooldown = cooldown_service or ParadigmCooldownService(store, clock)
        self._veto = veto_service or LonginusVetoService(client, store)
        self._adam = Agent(ADAM, client)
        self._lilith = Agent(LILITH, client)

    async def execute(self, query: str, key: str) -> ParadigmExecution:
        """Verifica cooldown e chave; executa Adam e Lilith concorrentemente ou penaliza."""
        cooldown_status = self._cooldown.status()
        if not cooldown_status.available:
            veto_result = await self._veto.check_veto(
                "Tentativa de uso do sistema Paradigm fora do protocolo de tempo."
            )
            self._cooldown.apply_penalty()
            return ParadigmExecution(
                query=query,
                available=False,
                cooldown_reason=cooldown_status.reason,
                veto=veto_result,
            )

        if not self._cooldown.validate_key(key):
            return ParadigmExecution(
                query=query,
                available=True,
                key_valid=False,
                cooldown_reason="Chave de autorização incorreta.",
            )

        adam_res, lilith_res = await asyncio.gather(
            self._adam.analyze(query),
            self._lilith.analyze(query),
        )
        assert isinstance(adam_res, PotentialAssessment)
        assert isinstance(lilith_res, AlignmentAssessment)

        self._cooldown.register_use()

        return ParadigmExecution(
            query=query,
            available=True,
            key_valid=True,
            adam=adam_res,
            lilith=lilith_res,
        )
