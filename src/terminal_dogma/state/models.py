"""Modelo de estado persistente unificado do Terminal Dogma (schema v2).

Substitui os dois arquivos da v1 (``dogma_registry.json`` e
``paradigm_lock.json``), que duplicavam a lógica de cooldown do Paradigm.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DogmaState(BaseModel):
    """Estado unificado e imutável do sistema.

    Atualizações são feitas via ``model_copy(update=...)`` seguidas de
    ``store.save(...)``, mantendo cada gravação validada pelo schema.
    """

    model_config = ConfigDict(frozen=True)

    schema_version: int = Field(default=2, ge=2, le=2)
    first_boot: datetime
    last_paradigm_use: datetime | None = None
    paradigm_uses: int = Field(default=0, ge=0)
    seele_interventions: int = Field(default=0, ge=0)
    longinus_activations: int = Field(default=0, ge=0)
    total_sessions: int = Field(default=0, ge=0)

    @classmethod
    def fresh(cls, now: datetime) -> "DogmaState":
        """Estado inicial de uma instalação nova."""
        return cls(first_boot=now)
