"""Migração dos dois arquivos de estado da v1 para o ``DogmaState`` unificado.

A v1 mantinha ``dogma_registry.json`` (persistence.py) e ``paradigm_lock.json``
(system.py) com lógicas de cooldown duplicadas. Regras de mesclagem:

- ``first_boot``: o mais antigo entre os dois arquivos (fallback: agora).
- ``last_paradigm_use``: o valor do lock (único efetivamente atualizado pela
  v1); se ausente, o do registry.
- Contadores: sempre do registry.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from terminal_dogma.state.clock import Clock, SystemClock
from terminal_dogma.state.models import DogmaState
from terminal_dogma.state.store import StateStore


def _read_json(path: Path | None) -> dict[str, Any]:
    """Lê um JSON legado de forma tolerante; qualquer falha retorna ``{}``."""
    if path is None:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _parse_counter(value: Any) -> int:
    return value if isinstance(value, int) and value >= 0 else 0


def migrate_legacy(
    registry_path: Path | None,
    lock_path: Path | None,
    *,
    clock: Clock | None = None,
) -> DogmaState:
    """Mescla ``dogma_registry.json`` + ``paradigm_lock.json`` em um estado v2.

    Nunca lança exceção: arquivos ausentes, corrompidos ou malformados
    degradam para um estado inicial novo.
    """
    registry = _read_json(registry_path)
    lock = _read_json(lock_path)

    candidates = [
        ts
        for ts in (
            _parse_timestamp(registry.get("first_boot")),
            _parse_timestamp(lock.get("project_creation_timestamp")),
        )
        if ts is not None
    ]
    first_boot = min(candidates) if candidates else (clock or SystemClock()).now()

    last_use = _parse_timestamp(lock.get("last_paradigm_usage_timestamp")) or _parse_timestamp(
        registry.get("last_paradigm_use")
    )

    return DogmaState(
        first_boot=first_boot,
        last_paradigm_use=last_use,
        paradigm_uses=_parse_counter(registry.get("paradigm_uses")),
        seele_interventions=_parse_counter(registry.get("seele_interventions")),
        longinus_activations=_parse_counter(registry.get("longinus_activations")),
        total_sessions=_parse_counter(registry.get("total_sessions")),
    )


def migrate_into(
    store: StateStore,
    registry_path: Path | None,
    lock_path: Path | None,
    *,
    clock: Clock | None = None,
) -> DogmaState:
    """Migra os arquivos legados e persiste o resultado no store fornecido."""
    state = migrate_legacy(registry_path, lock_path, clock=clock)
    store.save(state)
    return state
