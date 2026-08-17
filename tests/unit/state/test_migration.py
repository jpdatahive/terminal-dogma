"""Testes da migração dos dois arquivos de estado da v1 para o estado unificado."""

import json
from datetime import datetime

from terminal_dogma.state import (
    DogmaState,
    FixedClock,
    InMemoryStateStore,
    migrate_into,
    migrate_legacy,
)

NOW = datetime(2026, 8, 16, 12, 0, 0)

# Amostra real dos arquivos v1 versionados na raiz do repositório.
REGISTRY = {
    "first_boot": "2025-07-23T15:14:37.719457",
    "last_paradigm_use": None,
    "paradigm_uses": 0,
    "seele_interventions": 0,
    "longinus_activations": 0,
    "total_sessions": 35,
}
LOCK = {
    "project_creation_timestamp": "2025-07-23T18:15:16.909933",
    "last_paradigm_usage_timestamp": "2025-07-24T14:49:32.363735",
}


def _write(tmp_path, name, data):
    path = tmp_path / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class TestMergeRules:
    def test_mescla_arquivos_reais_da_v1(self, tmp_path):
        registry = _write(tmp_path, "dogma_registry.json", REGISTRY)
        lock = _write(tmp_path, "paradigm_lock.json", LOCK)

        state = migrate_legacy(registry, lock)

        # first_boot: o mais antigo entre os dois arquivos.
        assert state.first_boot == datetime(2025, 7, 23, 15, 14, 37, 719457)
        # last_paradigm_use: o lock é o arquivo efetivamente atualizado pela v1.
        assert state.last_paradigm_use == datetime(2025, 7, 24, 14, 49, 32, 363735)
        # Contadores vêm do registry.
        assert state.total_sessions == 35
        assert state.schema_version == 2

    def test_apenas_registry(self, tmp_path):
        registry = _write(tmp_path, "dogma_registry.json", REGISTRY)
        state = migrate_legacy(registry, None)
        assert state.first_boot == datetime(2025, 7, 23, 15, 14, 37, 719457)
        assert state.last_paradigm_use is None
        assert state.total_sessions == 35

    def test_apenas_lock(self, tmp_path):
        lock = _write(tmp_path, "paradigm_lock.json", LOCK)
        state = migrate_legacy(None, lock)
        assert state.first_boot == datetime(2025, 7, 23, 18, 15, 16, 909933)
        assert state.last_paradigm_use == datetime(2025, 7, 24, 14, 49, 32, 363735)
        assert state.total_sessions == 0

    def test_last_use_do_registry_quando_lock_nao_tem(self, tmp_path):
        registry = _write(
            tmp_path,
            "dogma_registry.json",
            {**REGISTRY, "last_paradigm_use": "2025-08-01T00:00:00"},
        )
        lock = _write(tmp_path, "paradigm_lock.json", {"project_creation_timestamp": None})
        state = migrate_legacy(registry, lock)
        assert state.last_paradigm_use == datetime(2025, 8, 1)


class TestTolerance:
    def test_arquivos_inexistentes_geram_estado_novo(self, tmp_path):
        state = migrate_legacy(
            tmp_path / "nope.json",
            tmp_path / "nada.json",
            clock=FixedClock(NOW),
        )
        assert state == DogmaState.fresh(NOW)

    def test_arquivos_corrompidos_geram_estado_novo(self, tmp_path):
        bad = tmp_path / "dogma_registry.json"
        bad.write_text("{{{", encoding="utf-8")
        state = migrate_legacy(bad, None, clock=FixedClock(NOW))
        assert state == DogmaState.fresh(NOW)

    def test_json_que_nao_e_objeto_e_ignorado(self, tmp_path):
        weird = _write(tmp_path, "dogma_registry.json", [1, 2, 3])
        state = migrate_legacy(weird, None, clock=FixedClock(NOW))
        assert state == DogmaState.fresh(NOW)

    def test_timestamps_e_contadores_invalidos_sao_ignorados(self, tmp_path):
        registry = _write(
            tmp_path,
            "dogma_registry.json",
            {"first_boot": "não-é-data", "total_sessions": "muito", "paradigm_uses": -3},
        )
        state = migrate_legacy(registry, None, clock=FixedClock(NOW))
        assert state.first_boot == NOW
        assert state.total_sessions == 0
        assert state.paradigm_uses == 0


def test_migrate_into_persiste_o_estado_migrado_no_store(tmp_path):
    registry = _write(tmp_path, "dogma_registry.json", REGISTRY)
    store = InMemoryStateStore(DogmaState.fresh(NOW))

    state = migrate_into(store, registry, None)

    assert store.load() == state
    assert state.total_sessions == 35
