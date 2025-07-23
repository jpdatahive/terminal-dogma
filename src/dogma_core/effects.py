"""
Módulo para efeitos visuais avançados
"""
import random
from rich.console import Console
from rich.text import Text
from time import sleep

class TerminalEffects:
    def __init__(self, console):
        self.console = console
        
    def show_loading(self, message, duration=3):
        """Exibe uma animação de carregamento"""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        with self.console.status("[bold]Processando...[/bold]") as status:
            for i in range(duration * 10):
                status.update(f"{frames[i % len(frames)]} {message}")
                sleep(0.1)
    
    def matrix_effect(self, duration=5):
        """Efeito de chuva de matriz"""
        chars = "01アイウエオカキクケコサシスセソ"
        width = self.console.width
        for _ in range(duration * 10):
            lines = []
            for _ in range(10):
                line = "".join(random.choice(chars) for _ in range(width))
                lines.append(f"[bright_green]{line}[/bright_green]")
            self.console.print("\n".join(lines), end="")
            sleep(0.1)
            self.console.clear()
    
    def at_field_effect(self):
        """Efeito de barreira AT"""
        self.console.print("[bright_cyan]" + "=" * self.console.width)
        for _ in range(5):
            self.console.print("[bright_cyan]||[/bright_cyan]" + " " * (self.console.width-4) + "[bright_cyan]||[/bright_cyan]")
        self.console.print("[bright_cyan]" + "=" * self.console.width)
        sleep(1)
