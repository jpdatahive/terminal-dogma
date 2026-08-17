"""Testes dos stores de estado (JSON atômico e em memória)."""

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pytest

from terminal_dogma.state import (
    DogmaState,
    FixedClock,
    InMemoryStateStore,
    JsonStateStore,
)

NOW = datetime(2026, 8, 16, 12, 0, 0)


class TestJsonStateStore:
    def test_load_em_arquivo_inexistente_cria_estado_inicial(self, tmp_path):
        store = JsonStateStore(tmp_path / "state.json", clock=FixedClock(NOW))
        state = store.load()
        assert state.first_boot == NOW
        assert state.paradigm_uses == 0
        assert (tmp_path / "state.json").exists()

    def test_round_trip_preserva_campos(self, tmp_path):
        store = JsonStateStore(tmp_path / "state.json", clock=FixedClock(NOW))
        state = store.load().model_copy(update={"paradigm_uses": 3, "total_sessions": 35})
        store.save(state)

        reloaded = JsonStateStore(tmp_path / "state.json").load()
        assert reloaded.paradigm_uses == 3
        assert reloaded.total_sessions == 35
        assert reloaded.first_boot == NOW

    def test_json_corrompido_vira_backup_e_estado_novo(self, tmp_path):
        path = tmp_path / "state.json"
        path.write_text("{ isso não é json", encoding="utf-8")

        store = JsonStateStore(path, clock=FixedClock(NOW))
        state = store.load()

        assert state.first_boot == NOW
        backup = tmp_path / "state.json.bak"
        assert backup.exists()
        assert backup.read_text(encoding="utf-8") == "{ isso não é json"

    def test_schema_invalido_vira_backup_e_estado_novo(self, tmp_path):
        path = tmp_path / "state.json"
        path.write_text(
            json.dumps({"schema_version": 99, "first_boot": "não é data"}),
            encoding="utf-8",
        )

        store = JsonStateStore(path, clock=FixedClock(NOW))
        state = store.load()

        assert state.first_boot == NOW
        assert (tmp_path / "state.json.bak").exists()

    def test_save_e_atomico_sem_arquivo_tmp_residual(self, tmp_path):
        path = tmp_path / "state.json"
        store = JsonStateStore(path, clock=FixedClock(NOW))
        store.save(store.load())
        assert not list(tmp_path.glob("*.tmp"))

    def test_falha_na_serializacao_limpa_tmp_e_propaga_erro(self, tmp_path, monkeypatch):
        path = tmp_path / "state.json"
        store = JsonStateStore(path, clock=FixedClock(NOW))
        store.load()

        def boom(_state, **_kwargs):
            raise RuntimeError("falha simulada de serialização")

        monkeypatch.setattr(DogmaState, "model_dump_json", boom)

        with pytest.raises(RuntimeError, match="falha simulada"):
            store.save(store.load())
        assert not list(tmp_path.glob("*.tmp"))

    def test_escritas_concorrentes_mantem_arquivo_valido(self, tmp_path):
        path = tmp_path / "state.json"
        store = JsonStateStore(path, clock=FixedClock(NOW))
        store.load()

        def write_session(n: int) -> None:
            store.save(store.load().model_copy(update={"total_sessions": n}))

        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(write_session, range(50)))

        # Independentemente da ordem dos escritores, o arquivo final é válido.
        final = store.load()
        assert 0 <= final.total_sessions < 50


class TestInMemoryStateStore:
    def test_estado_inicial_padrao_usa_clock(self):
        store = InMemoryStateStore(clock=FixedClock(NOW))
        assert store.load().first_boot == NOW

    def test_load_save_round_trip(self):
        store = InMemoryStateStore(DogmaState.fresh(NOW))
        store.save(store.load().model_copy(update={"seele_interventions": 7}))
        assert store.load().seele_interventions == 7
