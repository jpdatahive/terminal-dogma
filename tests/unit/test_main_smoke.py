"""Teste de fumaça do entry point do pacote."""

from unittest.mock import patch

from terminal_dogma.__main__ import main


def test_main_executa_app_textual():
    with patch("terminal_dogma.__main__.DogmaApp") as mock_app_cls:
        main()
        mock_app_cls.assert_called_once()
        mock_app_cls.return_value.run.assert_called_once()
