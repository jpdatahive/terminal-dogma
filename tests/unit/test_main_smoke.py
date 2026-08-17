"""Teste de fumaça do entry point do pacote (Fase 0)."""

from terminal_dogma import __version__
from terminal_dogma.__main__ import main


def test_main_imprime_banner_com_versao(capsys):
    main()
    out = capsys.readouterr().out
    assert "TERMINAL DOGMA" in out
    assert __version__ in out
