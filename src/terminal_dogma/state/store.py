"""Persistência do estado: ``StateStore`` (Protocol) + implementações."""

import json
import os
import tempfile
from pathlib import Path
from typing import Protocol

from pydantic import ValidationError

from terminal_dogma.state.clock import Clock, SystemClock
from terminal_dogma.state.models import DogmaState


class StateStore(Protocol):
    """Contrato de persistência do estado do sistema."""

    def load(self) -> DogmaState:
        """Carrega o estado atual (criando um inicial se necessário)."""
        ...

    def save(self, state: DogmaState) -> None:
        """Persiste o estado fornecido."""
        ...


class JsonStateStore:
    """Persiste o estado em JSON com escrita atômica (tmp + ``os.replace``).

    Arquivo inexistente gera estado inicial novo. Arquivo corrompido ou com
    schema inválido é preservado como ``<nome>.bak`` antes da recriação.
    """

    def __init__(self, path: Path, clock: Clock | None = None) -> None:
        self._path = Path(path)
        self._clock = clock or SystemClock()

    def load(self) -> DogmaState:
        try:
            return DogmaState.model_validate_json(self._path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return self._initialize()
        except (json.JSONDecodeError, ValidationError):
            os.replace(self._path, self._path.with_name(self._path.name + ".bak"))
            return self._initialize()

    def save(self, state: DogmaState) -> None:
        # tmp único por chamada (mesmo diretório = mesmo filesystem), para que
        # escritores concorrentes não colidam antes do rename atômico.
        fd, tmp_name = tempfile.mkstemp(
            dir=self._path.parent, prefix=self._path.name + ".", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(state.model_dump_json(indent=2))
        except BaseException:
            Path(tmp_name).unlink(missing_ok=True)
            raise
        os.replace(tmp_name, self._path)

    def _initialize(self) -> DogmaState:
        state = DogmaState.fresh(self._clock.now())
        self.save(state)
        return state


class InMemoryStateStore:
    """Store volátil, usado em testes e na composição de serviços."""

    def __init__(self, initial: DogmaState | None = None, clock: Clock | None = None) -> None:
        self._state = initial or DogmaState.fresh((clock or SystemClock()).now())

    def load(self) -> DogmaState:
        return self._state

    def save(self, state: DogmaState) -> None:
        self._state = state
