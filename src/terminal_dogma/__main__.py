"""Ponto de entrada do CLI ``dogma``."""

from terminal_dogma.tui.app import DogmaApp


def main() -> None:
    """Executa a aplicação TUI do Terminal Dogma."""
    app = DogmaApp()
    app.run()


if __name__ == "__main__":
    main()
