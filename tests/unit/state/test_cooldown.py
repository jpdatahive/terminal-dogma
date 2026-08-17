"""Testes do serviço de cooldown do Paradigm (100 dias) e da chave horária."""

import hashlib
from datetime import datetime, timedelta

import time_machine

from terminal_dogma.state import (
    DogmaState,
    FixedClock,
    InMemoryStateStore,
    ParadigmCooldownService,
    SystemClock,
)

BOOT = datetime(2026, 1, 1, 10, 0, 0)


def _service(clock, **state_kwargs):
    state = DogmaState(first_boot=BOOT, **state_kwargs)
    return ParadigmCooldownService(InMemoryStateStore(state), clock)


class TestAvailability:
    def test_antes_da_maturacao_esta_indisponivel(self):
        clock = FixedClock(BOOT + timedelta(days=40))
        status = _service(clock).status()
        assert status.available is False
        assert status.days_remaining == 60
        assert "maturação" in status.reason

    def test_apos_maturacao_sem_uso_esta_disponivel(self):
        clock = FixedClock(BOOT + timedelta(days=100))
        status = _service(clock).status()
        assert status.available is True
        assert status.days_remaining == 0
        assert "pronto" in status.reason

    def test_uso_recente_recoloca_em_cooldown(self):
        last_use = BOOT + timedelta(days=150)
        clock = FixedClock(last_use + timedelta(days=30))
        status = _service(clock, last_paradigm_use=last_use, paradigm_uses=1).status()
        assert status.available is False
        assert status.days_remaining == 70
        assert "cooldown" in status.reason

    def test_cooldown_completo_apos_uso_libera(self):
        last_use = BOOT + timedelta(days=150)
        clock = FixedClock(last_use + timedelta(days=100))
        status = _service(clock, last_paradigm_use=last_use, paradigm_uses=1).status()
        assert status.available is True


class TestRegisterUseAndPenalty:
    def test_register_use_atualiza_timestamp_e_contador(self):
        now = BOOT + timedelta(days=200)
        clock = FixedClock(now)
        store = InMemoryStateStore(DogmaState(first_boot=BOOT))
        service = ParadigmCooldownService(store, clock)

        service.register_use()

        state = store.load()
        assert state.last_paradigm_use == now
        assert state.paradigm_uses == 1
        assert service.status().available is False

    def test_penalidade_reinicia_cronometro_sem_contabilizar_uso(self):
        now = BOOT + timedelta(days=200)
        clock = FixedClock(now)
        store = InMemoryStateStore(DogmaState(first_boot=BOOT, paradigm_uses=2))
        service = ParadigmCooldownService(store, clock)

        service.apply_penalty()

        state = store.load()
        assert state.last_paradigm_use == now
        assert state.paradigm_uses == 2
        assert service.status().days_remaining == 100


class TestHourlyKey:
    def test_chave_deterministica_para_a_hora(self):
        clock = FixedClock(datetime(2026, 8, 16, 15, 30, 0))
        service = _service(clock)
        expected = hashlib.md5(b"2026081615").hexdigest()[:8].upper()
        assert service.current_key() == expected

    def test_validate_key_tolerante_a_caixa_e_espacos(self):
        clock = FixedClock(BOOT)
        service = _service(clock)
        key = service.current_key()
        assert service.validate_key(key.lower()) is True
        assert service.validate_key(f"  {key}  ") is True
        assert service.validate_key("CHAVE-ERRADA") is False

    def test_chave_muda_na_hora_seguinte(self):
        clock = FixedClock(BOOT)
        service = _service(clock)
        key_before = service.current_key()
        clock.advance(timedelta(hours=1))
        assert service.current_key() != key_before


class TestSystemClockIntegration:
    def test_cooldown_real_cruza_os_100_dias_com_time_machine(self):
        store = InMemoryStateStore(DogmaState(first_boot=datetime.now()))
        service = ParadigmCooldownService(store, SystemClock())
        assert service.status().available is False

        with time_machine.travel(datetime.now() + timedelta(days=101)):
            assert service.status().available is True
