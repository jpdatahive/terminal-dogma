"""Serviço de status consolidado do sistema."""

from terminal_dogma.domain.models import SystemStatus
from terminal_dogma.state.clock import Clock
from terminal_dogma.state.cooldown import ParadigmCooldownService
from terminal_dogma.state.store import StateStore


class StatusService:
    """Consolida métricas operacionais e gerencia contadores de sessão."""

    def __init__(
        self,
        store: StateStore,
        clock: Clock,
        cooldown_service: ParadigmCooldownService | None = None,
    ) -> None:
        self._store = store
        self._clock = clock
        self._cooldown = cooldown_service or ParadigmCooldownService(store, clock)

    def get_status(self) -> SystemStatus:
        """Gera uma fotografia atual do estado do sistema."""
        state = self._store.load()
        now = self._clock.now()
        days_since_boot = (now - state.first_boot).days
        cooldown_status = self._cooldown.status()

        return SystemStatus(
            days_since_boot=days_since_boot,
            can_use_paradigm=cooldown_status.available,
            days_until_paradigm=cooldown_status.days_remaining,
            paradigm_key=self._cooldown.current_key(),
            paradigm_uses=state.paradigm_uses,
            seele_interventions=state.seele_interventions,
            longinus_activations=state.longinus_activations,
            total_sessions=state.total_sessions,
        )

    def increment_session(self) -> int:
        """Registra uma nova sessão de comando e retorna o total atualizado."""
        state = self._store.load()
        new_total = state.total_sessions + 1
        self._store.save(state.model_copy(update={"total_sessions": new_total}))
        return new_total
