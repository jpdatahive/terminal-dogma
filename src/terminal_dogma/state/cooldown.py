"""Serviço de cooldown do sistema Paradigm e chave horária de autorização.

Regras (herdadas da v1, agora em um único lugar):
- O Paradigm exige 100 dias de maturação desde o primeiro boot.
- Cada uso legítimo inicia um novo ciclo de 100 dias.
- Uso indevido (fora do protocolo) aplica penalidade: reinicia o cronômetro
  sem contabilizar uso.
- A chave de autorização é o MD5 horário (AAAAMMDDHH), revelado via status.
"""

import hashlib
from dataclasses import dataclass
from typing import ClassVar

from terminal_dogma.state.clock import Clock
from terminal_dogma.state.store import StateStore


@dataclass(frozen=True)
class CooldownStatus:
    """Fotografia da disponibilidade do Paradigm em um instante."""

    available: bool
    days_remaining: int
    reason: str


class ParadigmCooldownService:
    """Regras temporais do Paradigm sobre um ``StateStore`` e um ``Clock``."""

    COOLDOWN_DAYS: ClassVar[int] = 100

    def __init__(self, store: StateStore, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    def status(self) -> CooldownStatus:
        """Calcula a disponibilidade atual (maturação + cooldown pós-uso)."""
        now = self._clock.now()
        state = self._store.load()

        days_since_boot = (now - state.first_boot).days
        if days_since_boot < self.COOLDOWN_DAYS:
            remaining = self.COOLDOWN_DAYS - days_since_boot
            return CooldownStatus(
                available=False,
                days_remaining=remaining,
                reason=(
                    f"Acesso negado. O sistema Progenitor requer {self.COOLDOWN_DAYS} dias "
                    f"de maturação após a inicialização ({remaining} restantes)."
                ),
            )

        if state.last_paradigm_use is not None:
            days_since_use = (now - state.last_paradigm_use).days
            if days_since_use < self.COOLDOWN_DAYS:
                remaining = self.COOLDOWN_DAYS - days_since_use
                return CooldownStatus(
                    available=False,
                    days_remaining=remaining,
                    reason=(
                        f"Acesso negado. O sistema está em cooldown por mais {remaining} dias."
                    ),
                )

        return CooldownStatus(
            available=True,
            days_remaining=0,
            reason="Sistema Paradigm pronto para ativação.",
        )

    def register_use(self) -> None:
        """Registra um uso legítimo: reinicia o ciclo e contabiliza o uso."""
        state = self._store.load()
        self._store.save(
            state.model_copy(
                update={
                    "last_paradigm_use": self._clock.now(),
                    "paradigm_uses": state.paradigm_uses + 1,
                }
            )
        )

    def apply_penalty(self) -> None:
        """Penalidade por uso indevido: reinicia o cronômetro sem contar uso."""
        state = self._store.load()
        self._store.save(state.model_copy(update={"last_paradigm_use": self._clock.now()}))

    def current_key(self) -> str:
        """Chave horária do Paradigm: MD5 de AAAAMMDDHH, 8 chars maiúsculos."""
        now = self._clock.now()
        seed = f"{now.year}{now.month:02d}{now.day:02d}{now.hour:02d}"
        return hashlib.md5(seed.encode()).hexdigest()[:8].upper()

    def validate_key(self, provided_key: str) -> bool:
        """Confere a chave informada com a da hora corrente."""
        return provided_key.strip().upper() == self.current_key()
