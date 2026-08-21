"""Widgets temáticos para a interface de usuário Textual do Terminal Dogma."""

from rich.align import Align
from rich.columns import Columns
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widget import Widget

from terminal_dogma.domain.models import (
    AgentDossier,
    DialectDebate,
    MagiDeliberation,
    ParadigmExecution,
    SeeleReport,
    SystemStatus,
    VetoResult,
)
from terminal_dogma.services.status import StatusService

JAPANESE_TERMS = {
    "system": "システム",
    "core": "コア",
    "analysis": "分析",
    "decision": "決定",
    "alert": "警告",
    "directive": "指令",
    "sync": "シンクロ",
    "pattern": "パターン",
    "emergency": "緊急事態",
    "welcome": "ようこそ",
}


class HeaderWidget(Widget):
    """Cabeçalho temático NERV / Central Dogma."""

    def render(self) -> RenderableType:
        title = Text()
        title.append("TERMINAL DOGMA ", style="bold red")
        title.append(
            f"— 中央ドグマ {JAPANESE_TERMS['system']} (NERV MAGI CORE)",
            style="bold cyan",
        )
        return Panel(Align.center(title), border_style="red")


class StatusBar(Widget):
    """Barra de status em tempo real com métricas e cooldown do Paradigm."""

    def __init__(
        self,
        status_service: StatusService,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._status_service = status_service

    def render(self) -> RenderableType:
        status = self._status_service.get_status()
        bar = Text()

        bar.append(" OPERAÇÃO: ", style="dim")
        bar.append(f"{status.days_since_boot}d ", style="bold cyan")
        bar.append("│ SESSÕES: ", style="dim")
        bar.append(f"{status.total_sessions:03d} ", style="bold yellow")
        bar.append("│ SEELE: ", style="dim")
        bar.append(f"{status.seele_interventions} ", style="bold magenta")
        bar.append("│ LONGINUS: ", style="dim")
        bar.append(f"{status.longinus_activations} ", style="bold red")

        bar.append("│ PARADIGM: ", style="dim")
        if status.can_use_paradigm:
            bar.append("PRONTO ", style="bold green")
        else:
            bar.append(
                f"RECALIBRANDO ({status.days_until_paradigm}d) ",
                style="bold yellow",
            )

        bar.append("│ CHAVE: ", style="dim")
        bar.append(f"[{status.paradigm_key}]", style="bold green")

        return Panel(bar, border_style="green", padding=(0, 1))


class HelpWidget(Widget):
    """Painel de referência de comandos do sistema."""

    def render(self) -> RenderableType:
        table = Table(box=None, expand=True, show_header=True)
        table.add_column("Comando", style="bold cyan", width=36)
        table.add_column("Descrição", style="white")

        table.add_row(
            "magi <consulta>",
            "Deliberação tripartite MAGI (Melchior, Balthasar, Casper)",
        )
        table.add_row(
            "seele <consulta>",
            "Análise explícita de risco pessimista do comitê SEELE",
        )
        table.add_row(
            "paradigm [<chave>] <consulta>",
            "Simulação Progenitora (ADAM vs. LILITH)",
        )
        table.add_row(
            "veto <consulta>",
            "Verificação direta contra as regras da Lança de Longinus",
        )
        table.add_row(
            "dialect <agente1> <agente2> <consulta>",
            "Debate dialético em rodadas entre unidades MAGI",
        )
        table.add_row(
            "dossier <agente_id>",
            "Exibe o perfil e diretriz central de um agente",
        )
        table.add_row(
            "status",
            "Exibe o relatório operacional e métricas completas",
        )
        table.add_row("clear", "Limpa a área de histórico da tela")
        table.add_row("exit / quit / sair", "Encerra a conexão com o Central Dogma")

        title = (
            f"[bold blue]TERMINAL DOGMA — GUIA DE COMANDOS ({JAPANESE_TERMS['system']})[/bold blue]"
        )
        return Panel(table, title=title, border_style="blue")


class StatusWidget(Widget):
    """Painel detalhado com o estado do sistema."""

    def __init__(
        self,
        status: SystemStatus,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.status = status

    def render(self) -> RenderableType:
        table = Table.grid(expand=True, padding=(0, 2))
        table.add_column(style="bold cyan")
        table.add_column(style="white")
        table.add_column(style="bold cyan")
        table.add_column(style="white")

        p_status = (
            "[bold green]PRONTO[/bold green]"
            if self.status.can_use_paradigm
            else f"[bold yellow]RECALIBRANDO ({self.status.days_until_paradigm}d)[/bold yellow]"
        )

        table.add_row(
            "Dias Operacionais:",
            str(self.status.days_since_boot),
            "Paradigm Status:",
            p_status,
        )
        table.add_row(
            "Total de Sessões:",
            str(self.status.total_sessions),
            "Chave Horária MD5:",
            f"[bold green]{self.status.paradigm_key}[/bold green]",
        )
        table.add_row(
            "Intervenções SEELE:",
            f"[magenta]{self.status.seele_interventions}[/magenta]",
            "Usos de Paradigm:",
            str(self.status.paradigm_uses),
        )
        table.add_row(
            "Ativações Longinus:",
            f"[red]{self.status.longinus_activations}[/red]",
            "Integridade Central:",
            "[bold green]100% OPERACIONAL[/bold green]",
        )

        return Panel(
            table,
            title=f"[bold green]RELATÓRIO DE STATUS — {JAPANESE_TERMS['system']}[/bold green]",
            border_style="green",
        )


class DossierWidget(Widget):
    """Exibe o dossiê detalhado de um agente."""

    def __init__(
        self,
        dossier: AgentDossier,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.dossier = dossier

    def render(self) -> RenderableType:
        content = Text()
        content.append(f"{self.dossier.title}\n", style="bold")
        content.append(f"Ativação: {self.dossier.activation_date}\n\n", style="dim")
        content.append(f"{self.dossier.description}\n\n", style="default")
        content.append("DIRETIVA CENTRAL:\n", style="bold")
        content.append(f"{self.dossier.core_directive}", style="italic")

        border_color = self.dossier.color.split()[-1]
        return Panel(
            content,
            title=f"[{self.dossier.color}]DOSSIÊ: {self.dossier.name}[/{self.dossier.color}]",
            border_style=border_color,
        )


class VetoWidget(Widget):
    """Exibe o resultado da verificação da Lança de Longinus."""

    def __init__(
        self,
        result: VetoResult,
        query_text: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.result = result
        self.query_text = query_text

    def render(self) -> RenderableType:
        if self.result.vetoed:
            text = Text()
            text.append(
                "⚠️  PROTOCOLO DE VETO ATIVADO — LANÇA DE LONGINUS  ⚠️\n\n",
                style="bold red",
            )
            rule = self.result.violated_rule or "Violação de protocolo."
            text.append(f"Regra Violada: {rule}\n", style="bold yellow")
            text.append(
                "Deliberação bloqueada por salvaguarda absoluta.",
                style="dim",
            )
            return Panel(
                Align.center(text),
                title="[bold red]LONGINUS VETO TRIGGERED[/bold red]",
                border_style="red",
            )

        text = Text()
        text.append("NENHUM VETO DETECTADO\n", style="bold green")
        text.append(
            "A consulta está dentro dos limites de segurança invioláveis.",
            style="dim",
        )
        return Panel(
            Align.center(text),
            title="[bold green]LONGINUS PROTOCOL — CLEAR[/bold green]",
            border_style="green",
        )


class SeeleWidget(Widget):
    """Exibe o relatório de risco do comitê SEELE."""

    def __init__(
        self,
        report: SeeleReport,
        is_intervention: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.report = report
        self.is_intervention = is_intervention or report.intervention

    def render(self) -> RenderableType:
        content = Text()
        if self.is_intervention:
            content.append("🚨  INTERVENÇÃO SEELE DETECTADA  🚨\n\n", style="bold red")
            content.append(f"{self.report.analysis}\n\n", style="italic")
            if self.report.alert:
                content.append(f"ALERTA: {self.report.alert}", style="bold red")
            return Panel(
                content,
                title="[bold magenta]SEELE :: INTERVENÇÃO DE EMERGÊNCIA[/bold magenta]",
                border_style="red",
            )

        content.append(f"{self.report.analysis}\n\n", style="default")
        if self.report.alert:
            content.append(f"ALERTA: {self.report.alert}", style="bold yellow")
        return Panel(
            content,
            title="[bold magenta]SEELE :: RELATÓRIO DE RISCO[/bold magenta]",
            border_style="magenta",
        )


class MagiDeliberationWidget(Widget):
    """Exibe a deliberação completa do conselho MAGI."""

    def __init__(
        self,
        deliberation: MagiDeliberation,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.deliberation = deliberation

    def render(self) -> RenderableType:
        if self.deliberation.vetoed:
            text = Text()
            text.append(
                "⚠️  DELIBERAÇÃO MAGI CANCELADA — VETO DE LONGINUS  ⚠️\n\n",
                style="bold red",
            )
            rule = self.deliberation.veto.violated_rule or "Violação de protocolo."
            text.append(f"Regra: {rule}\n", style="bold yellow")
            return Panel(
                Align.center(text),
                title="[bold red]DELIBERAÇÃO CANCELADA[/bold red]",
                border_style="red",
            )

        panels = []
        agent_names = {
            "melchior-01": ("MELCHIOR-01 (Cientista)", "bold blue", "blue"),
            "balthasar-02": ("BALTHASAR-02 (Mãe/Ética)", "bold green", "green"),
            "casper-03": ("CASPER-03 (Mulher/Pragmatismo)", "bold yellow", "yellow"),
        }

        for agent_id, analysis in self.deliberation.analyses.items():
            name, color, border = agent_names.get(agent_id, (agent_id.upper(), "white", "white"))
            vote_str = analysis.vote.value if analysis.vote else "INDETERMINADO"
            if vote_str == "POSITIVO":
                vote_style = "bold green"
            elif vote_str == "NEGATIVO":
                vote_style = "bold red"
            else:
                vote_style = "bold yellow"

            txt = Text()
            txt.append(f"{analysis.analysis}\n\n", style="default")
            txt.append("VOTO: ", style="bold")
            txt.append(vote_str, style=vote_style)

            panels.append(Panel(txt, title=f"[{color}]{name}[/{color}]", border_style=border))

        pos = self.deliberation.positive_votes
        neg = self.deliberation.negative_votes
        decision_text = Text()
        if self.deliberation.approved:
            decision_text.append(
                f"多数決による承認 — APROVADO POR MAIORIA ({pos} x {neg})",
                style="bold green",
            )
        else:
            decision_text.append(
                f"多数決による拒否 — REJEITADO ({pos} x {neg})",
                style="bold red",
            )

        if self.deliberation.is_unanimous:
            decision_text.append(" [UNÂNIME]", style="bold yellow")

        decision_panel = Panel(
            Align.center(decision_text),
            title=f"[bold blue]DECISÃO DO CONSELHO MAGI ({JAPANESE_TERMS['decision']})[/bold blue]",
            border_style="blue",
        )

        title = (
            f"[bold blue]M.A.G.I. {JAPANESE_TERMS['core']} — "
            f"DELIBERAÇÃO: '{self.deliberation.query}'[/bold blue]"
        )
        return Panel(
            Columns([*panels, decision_panel], equal=False, expand=True),
            title=title,
            border_style="blue",
        )


class ParadigmWidget(Widget):
    """Exibe o resultado da simulação Progenitora (ADAM vs. LILITH)."""

    def __init__(
        self,
        result: ParadigmExecution,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.result = result

    def render(self) -> RenderableType:
        if not self.result.available:
            txt = Text()
            txt.append("⚠️  ACESSO NEGADO AO SISTEMA PARADIGM  ⚠️\n\n", style="bold red")
            txt.append(f"{self.result.cooldown_reason}\n\n", style="yellow")
            txt.append(
                "Penalidade aplicada: o ciclo de resfriamento foi reiniciado.",
                style="dim",
            )
            return Panel(
                Align.center(txt),
                title="[bold red]PARADIGM LOCKDOWN[/bold red]",
                border_style="red",
            )

        if not self.result.key_valid:
            txt = Text()
            txt.append("⚠️  CHAVE DE AUTORIZAÇÃO INVÁLIDA  ⚠️\n\n", style="bold red")
            txt.append(f"{self.result.cooldown_reason}\n", style="yellow")
            txt.append(
                "Consulte a chave horária atual através do comando 'status'.",
                style="dim",
            )
            return Panel(
                Align.center(txt),
                title="[bold yellow]AUTHORIZATION FAILED[/bold yellow]",
                border_style="yellow",
            )

        adam_txt = Text()
        if self.result.adam:
            adam_txt.append(f"{self.result.adam.analysis}\n\n", style="default")
            adam_txt.append("POTENCIAL: ", style="bold")
            pot = self.result.adam.potential
            pot_val = pot.value if pot else "INDETERMINADO"
            adam_txt.append(pot_val, style="bold cyan")

        lilith_txt = Text()
        if self.result.lilith:
            lilith_txt.append(f"{self.result.lilith.analysis}\n\n", style="default")
            lilith_txt.append("ALINHAMENTO: ", style="bold")
            aln = self.result.lilith.alignment
            aln_val = aln.value if aln else "INDETERMINADO"
            lilith_txt.append(aln_val, style="bold white")

        adam_panel = Panel(
            adam_txt,
            title="[bold cyan]ADAM :: POTENCIAL DISRUPTIVO[/bold cyan]",
            border_style="cyan",
        )
        lilith_panel = Panel(
            lilith_txt,
            title="[bold white]LILITH :: IMPACTO E ALINHAMENTO[/bold white]",
            border_style="white",
        )

        title = (
            f"[bold cyan]SIMULAÇÃO PROGENITORA (ADAM vs. LILITH) — "
            f"'{self.result.query}'[/bold cyan]"
        )
        return Panel(
            Columns([adam_panel, lilith_panel], equal=True, expand=True),
            title=title,
            border_style="cyan",
        )


class DialectWidget(Widget):
    """Exibe o debate dialético entre duas unidades MAGI."""

    def __init__(
        self,
        debate: DialectDebate,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.debate = debate

    def render(self) -> RenderableType:
        panels = []
        for r in self.debate.rounds:
            v_a = r.agent_a_analysis.vote.value if r.agent_a_analysis.vote else "N/A"
            v_b = r.agent_b_analysis.vote.value if r.agent_b_analysis.vote else "N/A"

            txt = Text()
            txt.append(f"[{self.debate.agent_a_id.upper()}]\n", style="bold blue")
            txt.append(f"{r.agent_a_analysis.analysis}\n", style="default")
            txt.append(f"Voto: {v_a}\n\n", style="dim")

            txt.append(f"[{self.debate.agent_b_id.upper()}]\n", style="bold green")
            txt.append(f"{r.agent_b_analysis.analysis}\n", style="default")
            txt.append(f"Voto: {v_b}", style="dim")

            panels.append(
                Panel(
                    txt,
                    title=f"[bold yellow]Rodada {r.round_number}[/bold yellow]",
                    border_style="yellow",
                )
            )

        title = (
            f"[bold yellow]DEBATE DIALÉTICO ({self.debate.agent_a_id} vs "
            f"{self.debate.agent_b_id}) — '{self.debate.query}'[/bold yellow]"
        )
        return Panel(
            Columns(panels, equal=True, expand=True),
            title=title,
            border_style="yellow",
        )


class ErrorWidget(Widget):
    """Exibe mensagens de erro ou comandos inválidos."""

    def __init__(
        self,
        message: str,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.message = message

    def render(self) -> RenderableType:
        text = Text()
        text.append(f"ERRO: {self.message}\n", style="bold red")
        text.append(
            f"{JAPANESE_TERMS['system']} — Digite 'help' para ver os comandos.",
            style="dim",
        )
        return Panel(text, title="[bold red]FALHA DE COMANDO[/bold red]", border_style="red")


class ProcessingWidget(Widget):
    """Exibe indicador visual de deliberação em andamento."""

    def __init__(
        self,
        command_label: str,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.command_label = command_label

    def render(self) -> RenderableType:
        text = Text()
        text.append("⚡ SINCRONIZANDO COM O CENTRAL DOGMA... ", style="bold yellow")
        text.append(f"[{self.command_label}]\n", style="dim")
        text.append(
            "Conectando aos agentes neurais e processando deliberação...",
            style="italic cyan",
        )
        return Panel(text, border_style="yellow")
