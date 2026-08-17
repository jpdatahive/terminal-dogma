"""Ponto de entrada do CLI ``dogma``.

Placeholder até a Fase 6 (TUI com Textual). Por ora apenas confirma que a
instalação do pacote e do entry point funcionam.
"""

from terminal_dogma import __version__


def main() -> None:
    """Exibe o banner de versão do sistema."""
    print(f"TERMINAL DOGMA v{__version__} — sistema em reconstrução.")


if __name__ == "__main__":
    main()
