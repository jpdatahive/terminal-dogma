"""Testes das exceções temáticas de domínio."""

import pytest

from terminal_dogma.domain.exceptions import (
    AngelPatternDetected,
    ATFieldInterference,
    CentralDogmaLockdown,
    DogmaSystemException,
)


def test_at_field_interference_carrega_nome_do_agente():
    exc = ATFieldInterference("MELCHIOR-01")
    assert exc.agent_name == "MELCHIOR-01"
    assert "MELCHIOR-01" in str(exc)


def test_central_dogma_lockdown_carrega_subsistema():
    exc = CentralDogmaLockdown("SEELE")
    assert exc.subsystem == "SEELE"
    assert "SEELE" in str(exc)


def test_angel_pattern_detected_carrega_mensagem():
    exc = AngelPatternDetected("padrão azul")
    assert "padrão azul" in str(exc)


@pytest.mark.parametrize(
    "exc",
    [ATFieldInterference(), CentralDogmaLockdown(), AngelPatternDetected()],
)
def test_todas_derivam_da_base_tematica(exc):
    assert isinstance(exc, DogmaSystemException)
