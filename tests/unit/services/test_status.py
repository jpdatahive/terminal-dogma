"""Testes do serviço de status consolidado do sistema."""

from datetime import datetime, timedelta

from terminal_dogma.services.status import StatusService
from terminal_dogma.state import DogmaState, FixedClock, InMemoryStateStore

BOOT = datetime(2026, 1, 1, 10, 0, 0)


class TestStatusService:
    def test_status_retorna_metricas_completas(self):
        clock = FixedClock(BOOT + timedelta(days=120))
        state = DogmaState(
            first_boot=BOOT,
            last_paradigm_use=BOOT + timedelta(days=110),
            paradigm_uses=1,
            seele_interventions=2,
            longinus_activations=1,
            total_sessions=15,
        )
        store = InMemoryStateStore(state)
        service = StatusService(store, clock)

        status = service.get_status()

        assert status.days_since_boot == 120
        assert status.can_use_paradigm is False
        assert status.days_until_paradigm == 90
        assert status.paradigm_uses == 1
        assert status.seele_interventions == 2
        assert status.longinus_activations == 1
        assert status.total_sessions == 15
        assert len(status.paradigm_key) == 8

    def test_increment_session_atualiza_contador(self):
        clock = FixedClock(BOOT)
        store = InMemoryStateStore(DogmaState(first_boot=BOOT, total_sessions=5))
        service = StatusService(store, clock)

        new_total = service.increment_session()

        assert new_total == 6
        assert store.load().total_sessions == 6
