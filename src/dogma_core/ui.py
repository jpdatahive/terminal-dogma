import sys
import os
import time
import random
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.columns import Columns
from rich.rule import Rule
import codecs


# Force UTF-8 encoding
if sys.platform == "win32":
    os.system("chcp 65001 > nul")  # Windows

# Mapeamento de cores para cada agente para manter a consistência visual
AGENT_COLORS = {
    "MAGI": "bold blue",
    "MELCHIOR-01": "bold blue",
    "BALTHASAR-02": "bold green", 
    "CASPER-03": "bold yellow",
    "SEELE": "bold magenta",
    "PARADIGM": "bold cyan",
    "ADAM_CATALYST": "bold cyan",
    "LILITH_FOUNDATION": "bold white",
    "LONGINUS": "bold red",
    "GENDO": "bold red",
}

# Textos em japonês para autenticidade
JAPANESE_TERMS = {
    "welcome": "ようこそ",  # Bem-vindo
    "system": "システム",   # Sistema
    "operational": "作動中", # Operacional
    "analysis": "分析",     # Análise
    "decision": "決定",     # Decisão
    "alert": "警告",       # Alerta
    "directive": "指令",    # Diretiva
    "core": "コア",        # Core
    "sync": "シンクロ",     # Sincronização
    "pattern": "パターン",   # Padrão
    "angel": "使徒",       # Anjo/Angel
    "eva": "エヴァ",       # Eva
    "nerv": "ネルフ",      # NERV
    "activate": "起動",     # Ativar
    "emergency": "緊急事態", # Emergência
}

AGENT_DOSSIERS = {
    "melchior-01": {
        "name": "MELCHIOR-01",
        "title": "第一の賢者、メルキオール (O Primeiro Homem Sábio)",
        "color": "bold blue",
        "description": "A unidade de supercomputador focada em [bold]lógica pura, análise de dados e raciocínio científico[/bold]. Melchior processa informações de forma empírica, avaliando a viabilidade e as consequências causais diretas. Sua personalidade é fria, analítica e desprovida de emoção.",
        "activation_date": "2042-08-15",
        "core_directive": "全ての事象を観測し、記録し、予測する (Observar, registrar e prever todos os fenômenos)."
    },
    "balthasar-02": {
        "name": "BALTHASAR-02",
        "title": "第二の賢者、バルタザール (O Segundo Homem Sábio)",
        "color": "bold green",
        "description": "A unidade de supercomputador responsável pela [bold]análise humanística, moral e ética[/bold]. Balthasar avalia o impacto das decisões no bem-estar humano, nos valores sociais e na dignidade individual. Sua personalidade é empática, ponderada e sábia.",
        "activation_date": "2042-09-21",
        "core_directive": "人類の調和と存続を最優先する (Priorizar a harmonia e a sobrevivência da humanidade)."
    },
    "casper-03": {
        "name": "CASPER-03",
        "title": "第三の賢者、カスパー (O Terceiro Homem Sábio)",
        "color": "bold yellow",
        "description": "A unidade de supercomputador que lida com [bold]análise estratégica, pragmatismo e execução[/bold]. Casper foca na viabilidade, alocação de recursos, riscos operacionais e no resultado prático das decisões. Sua personalidade é direta, realista e focada em resultados.",
        "activation_date": "2042-10-05",
        "core_directive": "最も効率的な手段で目的を達成する (Alcançar o objetivo pelos meios mais eficientes)."
    },
    "seele": {
        "name": "SEELE_INTERJECTOR",
        "title": "ゼーレ (Alma)",
        "color": "bold magenta",
        "description": "Um sistema de vigilância oculto que representa os interesses do comitê SEELE. Sua função é a [bold]análise de risco pessimista, identificando consequências não intencionais, piores cenários e interesses ocultos[/bold]. Opera com ceticismo e assume segundas intenções em todas as propostas.",
        "activation_date": "Desconhecida",
        "core_directive": "シナリオを維持し、人類の補完を遂行する (Manter o cenário e executar a instrumentalização humana)."
    },
    # Adicione outros agentes aqui no futuro
}

class UIController:
    """
    Gerencia toda a saída visual para o terminal usando a biblioteca Rich.
    Cria uma experiência imersiva e temática para cada subsistema do Terminal Dogma.
    """

    def __init__(self):
        # Force UTF-8 for console
        self.console = Console(force_terminal=True, legacy_windows=False)
        self.terminal_width = self.console.size.width
        self._generate_headers()


    def _sanitize_text(self, text: str) -> str:
        """
        Sanitiza o texto para exibição segura no console, substituindo 
        surrogates inválidos e outros caracteres problemáticos.
        """
        if not isinstance(text, str):
            text = str(text)
        
        # A maneira mais robusta e padrão de lidar com surrogates inválidos
        # é codificar para bytes substituindo os erros e depois decodificar de volta para string.
        # Isso troca caracteres malformados por um caractere de substituição '',
        # evitando que o programa quebre.
        return text.encode('utf-8', errors='replace').decode('utf-8')

    def _generate_headers(self):
        """Cria e armazena todos os cabeçalhos ASCII para acesso rápido."""
        self.headers = {
            "MAIN": Text(f"""
████████╗███████╗██████╗ ███╗   ███╗██╗ ███╗   ██╗ █████╗ ██╗     
╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║ ████╗  ██║██╔══██╗██║     
   ██║   █████╗  ██████╔╝██╔████╔██║██║ ██╔██╗ ██║███████║██║     
   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║ ██║╚██╗██║██╔══██║██║     
   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║ ██║ ╚████║██║  ██║███████╗
   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
                    
                D O G M A   {JAPANESE_TERMS['system']}
            """, style="bold red"),
            "MAGI": Text(f"M.A.G.I. {JAPANESE_TERMS['core']} - メルキオール・バルタザール・カスパー", style="bold blue"),
            "SEELE": Text(f"[ 01 :: SOUND ONLY ] - {JAPANESE_TERMS['emergency']}", style="bold magenta"),
            "PARADIGM": Text(f"Progenitor Simulation: アダム vs. リリス - {JAPANESE_TERMS['pattern']} {JAPANESE_TERMS['analysis']}", style="bold cyan"),
            "LONGINUS": Text(f"ロンギヌスの槍 - Lance of Longinus - Veto Protocol", style="bold red"),
            "GENDO": Text(f"碇ゲンドウ - Gendo Ikari - Final {JAPANESE_TERMS['directive']}", style="bold red"),
        }

    def _get_responsive_width(self, content_type: str = "normal") -> int:
        """Calcula a largura responsiva baseada no tamanho do terminal."""
        terminal_width = self.console.size.width
        
        if content_type == "narrow":
            return min(60, terminal_width - 4)
        elif content_type == "wide":
            return min(120, terminal_width - 2)
        else:
            return min(80, terminal_width - 2)

    def _get_responsive_width(self, content_type: str = "normal") -> int:
        """Calcula a largura responsiva baseada no tamanho do terminal."""
        terminal_width = self.console.size.width
        
        # Usa quase toda a largura disponível, deixando margem mínima
        if content_type == "narrow":
            return max(60, terminal_width - 4)
        elif content_type == "wide":
            return terminal_width - 2  # Margem mínima
        else:
            return terminal_width - 4  # Margem pequena

    def display_system_header(self, system_name: str):
        """Exibe o cabeçalho centralizado usando largura total."""
        header = self.headers.get(system_name.upper(), self.headers["MAIN"])
        
        # Centraliza e usa largura total
        self.console.print(Panel(
            Align.center(header), 
            border_style=AGENT_COLORS.get(system_name.upper(), "white")
            # Remove width para usar largura total
        ))

    def display_boot_sequence(self):
        """Mostra uma sequência de boot animada para criar uma atmosfera imersiva."""
        self.console.clear()
        boot_messages = [
            f"セントラルドグマへの接続を確立中... ({JAPANESE_TERMS['activate']})",
            f"ゼーレプロトコルを確認中... (SEELE Protocol Check)",
            f"メルキオール認知マトリックス読み込み中... (MELCHIOR Matrix)",
            f"バルタザール共感エンジン読み込み中... (BALTHASAR Engine)",
            f"カスパー戦略コア読み込み中... (CASPER Core)",
            f"アダム＆リリスパラダイムアルゴリズム{JAPANESE_TERMS['sync']}中...",
            f"ロンギヌス拒否プロトコル武装中... (LONGINUS Armed)",
            f"全{JAPANESE_TERMS['system']}オンライン。ターミナルドグマへ{JAPANESE_TERMS['welcome']}。"
        ]

        with Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task("初期化中...", total=len(boot_messages))
            for message in boot_messages:
                progress.update(task, description=message)
                time.sleep(random.uniform(0.4, 0.9))
                progress.advance(task)
        
        self.console.clear()
        
        # Header principal responsivo
        width = self._get_responsive_width("wide")
        self.console.print(Panel(
            Align.center(self.headers["MAIN"]), 
            border_style="red",
            width=width
        ))
        
        welcome_panel = Panel(
f"""
[bold green]{JAPANESE_TERMS['welcome']}ターミナルドグマへ[/bold green]
[dim]人類の運命はここで決定される...[/dim]

コマンド [cyan]help[/cyan] で議決{JAPANESE_TERMS['system']}一覧を表示
Command [cyan]help[/cyan] for Deliberation Systems List
""",
            title=f"[bold red]{JAPANESE_TERMS['system']}準備完了[/bold red]",
            border_style="red",
            width=self._get_responsive_width("normal")
        )
        self.console.print(welcome_panel)

    def get_user_input(self, session_count: int) -> str:
        prompt_text = Text()
        prompt_text.append("DOGMA", style="bold red")
        prompt_text.append(f":{session_count:03d}> ", style="default")
        return self.console.input(prompt_text)

    def display_help(self):
        self.display_system_header("HELP")
        
        # Layout responsivo para help
        if self.console.size.width > 100:
            self._display_help_wide()
        else:
            self._display_help_narrow()

    def _display_help_wide(self):
        """Exibe help em layout amplo para terminais grandes."""
        help_content = f"""
[bold cyan]ターミナルドグマ議決{JAPANESE_TERMS['system']}[/bold cyan]
[bold cyan]TERMINAL DOGMA DELIBERATION SYSTEMS[/bold cyan]

Use um comando seguido por sua consulta (query).

[bold blue]magi <query>[/bold blue] - M.A.G.I.{JAPANESE_TERMS['core']}
議決: MAGIカウンシルによる複雑な決定の標準的な議決
Deliberação padrão do conselho MAGI para decisões complexas.

[bold magenta]seele <query>[/bold magenta] - ゼーレ{JAPANESE_TERMS['analysis']}
リスク{JAPANESE_TERMS['analysis']}: 悲観的なリスク{JAPANESE_TERMS['analysis']}。欠陥と最悪のシナリオを発見
Análise de risco pessimista. Encontra falhas e piores cenários.

[bold cyan]paradigm <query>[/bold cyan] - パラダイム比較
革新の可能性 (アダム) vs. 安定性への影響 (リリス) を比較
Compara potencial de inovação (Adam) vs. impacto na estabilidade (Lilith).

[bold red]veto <query>[/bold red] - ロンギヌス拒否
基本的な不可侵ルールに違反するかどうかをチェック
Verifica se uma proposta viola regras fundamentais invioláveis.

[bold yellow]dossier <agent_id>[/bold yellow] - エージェントのドシエ
特定のエージェントの詳細なプロフィールを表示
Exibe o perfil detalhado de um agente específico.

[bold green]diagnostic[/bold green] - システム診断
全てのサブシステムの診断シーケンスを実行
Executa uma sequência de diagnóstico em todos os subsistemas.

[bold red]gendo <query>[/bold red] - ゲンドウ最終{JAPANESE_TERMS['directive']}
全エージェントによる完全な{JAPANESE_TERMS['analysis']}を実行し、最終{JAPANESE_TERMS['directive']}を発行
Executa análise completa com todos os agentes e emite diretiva final.

[bold yellow]追加コマンド / ADDITIONAL COMMANDS:[/bold yellow]
- [cyan]status[/cyan] ({JAPANESE_TERMS['system']}状態), [cyan]clear[/cyan] (画面クリア), [cyan]exit[/cyan] (終了)
        """
        self.console.print(Panel(
            help_content, 
            title=f"[bold blue]{JAPANESE_TERMS['system']}ヘルプ[/bold blue]", 
            border_style="blue",
            width=self._get_responsive_width("wide")
        ))

    def _display_help_narrow(self):
        """Exibe help em layout estreito para terminais pequenos."""
        commands = [
            ("[bold blue]magi[/bold blue]", "MAGI議決 / MAGI Council"),
            ("[bold magenta]seele[/bold magenta]", "ゼーレリスク{JAPANESE_TERMS['analysis']} / SEELE Risk"),
            ("[bold cyan]paradigm[/bold cyan]", "パラダイム比較 / Paradigm Compare"),
            ("[bold red]veto[/bold red]", "ロンギヌス拒否 / Longinus Veto"),
            ("[bold red]gendo[/bold red]", "ゲンドウ{JAPANESE_TERMS['directive']} / Gendo Directive"),
        ]
        
        panels = []
        for cmd, desc in commands:
            panels.append(Panel(f"{cmd}\n{desc}", expand=True))
        
        self.console.print(Columns(panels, equal=True, expand=True))

    def display_status(self, status_data: dict):
        """Exibe o status detalhado do sistema com um layout temático aprimorado."""
        self.display_system_header("STATUS")

        # Layout principal com duas colunas
        layout = Layout()
        layout.split_column(
            Layout(name="main_metrics", size=12),
            Layout(name="paradigm_status")
        )

        # --- Coluna da Esquerda: Métricas Principais ---
        
        # Tabela de métricas do sistema
        system_metrics_table = Table.grid(expand=True, padding=(0, 2))
        system_metrics_table.add_column(style="bold cyan")
        system_metrics_table.add_column(style="white")
        system_metrics_table.add_row(f"{JAPANESE_TERMS['system']}稼働日数 (Dias Operacionais):", str(status_data['days_since_boot']))
        system_metrics_table.add_row(f"総セッション数 (Sessões Totais):", str(status_data['total_sessions']))
        system_metrics_table.add_row(f"ゼーレ介入 (Intervenções SEELE):", f"[magenta]{status_data['seele_interventions']}[/magenta]")
        system_metrics_table.add_row(f"ロンギヌス起動 (Ativações Longinus):", f"[red]{status_data['longinus_activations']}[/red]")

        # Tabela de status do MAGI
        magi_sync_rate = random.uniform(97.5, 99.9)
        at_field_stability = random.uniform(92.0, 99.9)
        magi_status_table = Table.grid(expand=True, padding=(0, 2))
        magi_status_table.add_column(style="bold yellow")
        magi_status_table.add_column(style="white")
        magi_status_table.add_row(f"MAGI{JAPANESE_TERMS['sync']}率 (Taxa de Sync):", f"{magi_sync_rate:.3f}%")
        magi_status_table.add_row("A.T.フィールド安定性 (Estabilidade):", f"[green]{at_field_stability:.2f}%[/green]")

        # Painel da esquerda
        left_panel = Panel(
            Columns([system_metrics_table, magi_status_table], equal=True, expand=True),
            title=f"[bold green]総合{JAPANESE_TERMS['system']}状態 - Relatório de Status[/bold green]",
            border_style="green"
        )

        # --- Coluna da Direita: Status do Paradigm ---

        if status_data['can_use_paradigm']:
            paradigm_status_text = "[bold green]起動準備完了 (PRONTO PARA ATIVAÇÃO)[/bold green]"
            paradigm_detail_text = f"登録された使用回数 (Usos Registrados): {status_data['paradigm_uses']}"
        else:
            paradigm_status_text = "[bold yellow]再調整中 (RECALIBRANDO)[/bold yellow]"
            paradigm_detail_text = f"次の起動まで (Próxima Ativação em): {status_data['days_until_paradigm']} 日 (dias)"

        right_panel = Panel(
            f"""
[bold cyan]Paradigm {JAPANESE_TERMS['system']} Status:[/bold cyan]
{paradigm_status_text}

[dim]{paradigm_detail_text}[/dim]
            """,
            title=f"[bold cyan]PARADIGM - {JAPANESE_TERMS['pattern']} {JAPANESE_TERMS['analysis']}[/bold cyan]",
            border_style="cyan"
        )

        # Monta o layout final
        # Para simplificar, vamos usar um layout de colunas em vez do layout complexo
        # que pode ter problemas de renderização dependendo do terminal.
        final_columns = Columns([left_panel, right_panel], equal=True, expand=True)
        self.console.print(final_columns)

    def display_dossier(self, agent_id: str):
        """Exibe o dossiê de um agente específico."""
        dossier = AGENT_DOSSIERS.get(agent_id.lower())
        if not dossier:
            self.display_error(f"Dossiê para o agente '{agent_id}' não encontrado.")
            return

        self.display_system_header(dossier["name"])

        panel_content = f"""
[bold]{dossier['title']}[/bold]
[dim]Data de Ativação: {dossier['activation_date']}[/dim]

---

[i]{dossier['description']}[/i]

---

[bold]Diretiva Central:[/bold]
[i]{dossier['core_directive']}[/i]
        """

        panel = Panel(
            panel_content,
            title=f"[b {dossier['color']}]DOSSIÊ DE AGENTE: {dossier['name']}[/b {dossier['color']}]",
            border_style=dossier['color'].split(' ')[1] if ' ' in dossier['color'] else dossier['color'],
            width=self._get_responsive_width("wide")
        )
        self.console.print(panel)

    def display_diagnostic(self):
        """Exibe uma sequência de diagnóstico para todos os sistemas."""
        self.display_system_header("DIAGNOSTIC")
        
        agents_to_check = [
            ("MELCHIOR-01", "Lógica de Dados"),
            ("BALTHASAR-02", "Matriz de Empatia"),
            ("CASPER-03", "Simulador Estratégico"),
            ("SEELE_INTERJECTOR", "Canal de Risco"),
            ("ADAM_CATALYST", "Potencial Disruptivo"),
            ("LILITH_FOUNDATION", "Núcleo Cultural"),
            ("LONGINUS_VETO", "Protocolo de Veto")
        ]

        self.console.print("Iniciando sequência de diagnóstico do sistema...", style="bold yellow")

        with Progress(
            SpinnerColumn(spinner_name="line"),
            TextColumn("[progress.description]{task.description}"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            for agent_name, description in agents_to_check:
                task = progress.add_task(f"Verificando {agent_name}...", total=100)
                while not progress.finished:
                    progress.update(task, advance=random.uniform(5, 15))
                    time.sleep(0.1)
                
                color = AGENT_COLORS.get(agent_name, "white").split(' ')[-1]
                final_status = "[bold green]オンライン (ONLINE)[/bold green]"
                self.console.print(f"-[{color}]{agent_name}[/{color}] ({description}): {final_status}")

        self.console.print("\n[bold green]診断完了。全てのシステムは正常に作動中です。[/bold green]", justify="center")
        self.console.print("[dim]Diagnostic complete. All systems are operational.[/dim]", justify="center")

    def display_agent_analysis(self, agent_name: str, result: dict):
        """Exibe análise de agente com elementos japoneses."""
        color = AGENT_COLORS.get(agent_name, "white")
        
        # Mapear nomes dos agentes para japonês
        japanese_names = {
            "MELCHIOR-01": "メルキオール-01",
            "BALTHASAR-02": "バルタザール-02", 
            "CASPER-03": "カスパー-03",
            "SEELE_INTERJECTOR": "ゼーレ介入",
            "ADAM_CATALYST": "アダム触媒",
            "LILITH_FOUNDATION": "リリス基盤",
            "LONGINUS_VETO": "ロンギヌス拒否"
        }
        
        jp_name = japanese_names.get(agent_name, agent_name)
        panel_title = f"[b {color}]{jp_name} - {JAPANESE_TERMS['analysis']}受信[/b {color}]"
        
        # Sanitiza o conteúdo com tratamento mais robusto
        try:
            analysis = self._sanitize_text(result.get('analysis', 'Análise não disponível'))
            verdict = self._sanitize_text(result.get('verdict', 'Veredito não disponível'))
            content = f"[i]{analysis}[/i]\n\n[b]{verdict}[/b]"
            
            # Testa se o conteúdo pode ser renderizado
            content.encode('utf-8')
            
        except Exception as e:
            # Fallback seguro se a sanitização falhar
            content = f"[red]Erro na exibição da análise do {agent_name}[/red]\n[dim]Conteúdo contém caracteres incompatíveis[/dim]"
        
        self.console.print(Align.center(Panel(
            content, 
            title=panel_title, 
            border_style=color.split(' ')[1] if ' ' in color else color
        )))

    def display_magi_decision(self, positivos: int, negativos: int):
        """Exibe decisão MAGI com texto japonês."""
        if positivos > negativos:
            decision = f"多数決による承認 ({positivos}対{negativos})"
            decision_en = "MAJORITY APPROVAL"
            color = "green"
        else:
            decision = f"多数決による拒否 ({positivos}対{negativos})"
            decision_en = "MAJORITY REJECTION" 
            color = "red"
            
        content = f"[bold {color}]{decision}[/bold {color}]\n[dim]{decision_en}[/dim]"
        
        self.console.print(Panel(
            content, 
            title=f"[bold blue]MAGIカウンシル{JAPANESE_TERMS['decision']}[/bold blue]",
            width=self._get_responsive_width("narrow")
        ))

    def display_seele_report(self, result: dict, is_intervention: bool = False):
        """Exibe relatório SEELE com elementos japoneses."""
        if is_intervention:
            title = f"[bold magenta]介入{JAPANESE_TERMS['alert']} - ゼーレ[/bold magenta]"
            border_color = "red"
            content = f"[bold]現在の問い合わせで差し迫ったリスクが検出されました。[/bold]\n[bold]IMMINENT RISK DETECTED IN CURRENT QUERY.[/bold]\n\n[i]{result['analysis']}[/i]\n\n[b]{result.get('verdict', 'Alert not specified.')}[/b]"
        else:
            title = f"[bold magenta]ゼーレリスク報告書[/bold magenta]"
            border_color = "magenta"
            content = f"[i]{result['analysis']}[/i]\n\n[b]{result.get('verdict', 'Alert not specified.')}[/b]"
        
        self.console.print(Panel(
            content, 
            title=title, 
            border_style=border_color,
            width=self._get_responsive_width("normal")
        ))

    def display_paradigm_comparison(self, adam_result: dict, lilith_result: dict):
        """Exibe comparação de paradigma com layout responsivo."""
        if self.console.size.width > 80:
            # Layout lado a lado para terminais grandes
            layout = Layout()
            layout.split_row(
                Layout(name="adam"),
                Layout(name="lilith"),
            )
            layout["adam"].update(Panel(
                f"[i]{adam_result['analysis']}[/i]\n\n[b]{adam_result['verdict']}[/b]", 
                title="[bold cyan]アダム: 破壊的可能性[/bold cyan]\n[dim]ADAM: DISRUPTIVE POTENTIAL[/dim]", 
                border_style="cyan"
            ))
            layout["lilith"].update(Panel(
                f"[i]{lilith_result['analysis']}[/i]\n\n[b]{lilith_result['verdict']}[/b]", 
                title="[bold white]リリス: 根本的影響[/bold white]\n[dim]LILITH: FUNDAMENTAL IMPACT[/dim]", 
                border_style="white"
            ))
            self.console.print(layout)
        else:
            # Layout vertical para terminais pequenos
            self.console.print(Panel(
                f"[i]{adam_result['analysis']}[/i]\n\n[b]{adam_result['verdict']}[/b]", 
                title="[bold cyan]アダム: 破壊的可能性[/bold cyan]", 
                border_style="cyan",
                width=self._get_responsive_width("normal")
            ))
            self.console.print(Panel(
                f"[i]{lilith_result['analysis']}[/i]\n\n[b]{lilith_result['verdict']}[/b]", 
                title="[bold white]リリス: 根本的影響[/bold white]", 
                border_style="white",
                width=self._get_responsive_width("normal")
            ))

    def display_longinus_veto(self, result: dict):
        """Exibe veto Longinus com elementos japoneses."""
        verdict = result['verdict']
        if "VETO ACIONADO" in verdict or "VETO" in verdict:
            content = Align.center(
                f"[bold red]プロトコル作動\nPROTOCOL ACTIVATED\n\nロンギヌスの槍 - 拒否\n{verdict}[/bold red]", 
                vertical="middle"
            )
            panel = Panel(content, border_style="red", height=9)
        else:
            content = Align.center(
                "[bold green]拒否検出なし\nNO VETO DETECTED[/bold green]", 
                vertical="middle"
            )
            panel = Panel(content, border_style="green", height=7)
        
        self.console.print(panel)

    def display_gendo_directive(self, synthesis: dict):
        """Exibe diretiva final do Gendo com elementos japoneses."""
        magi_decision = synthesis['magi_decision']
        decision_text = "承認" if int(magi_decision[0]) > int(magi_decision[2]) else "拒否"
        decision_en = "APPROVAL" if int(magi_decision[0]) > int(magi_decision[2]) else "REJECTION"
        
        content = f"""
MAGIカウンシル{JAPANESE_TERMS['decision']}: [b]{decision_text} ({synthesis['magi_decision']})[/b]
MAGI Council Decision: [b]{decision_en} ({synthesis['magi_decision']})[/b]

[u]質的要因 / Qualitative Factors:[/u]
- [cyan]破壊的可能性 (アダム):[/cyan] {synthesis['adam_verdict']}
- [white]根本的影響 (リリス):[/white] {synthesis['lilith_verdict']}
- [magenta]リスク{JAPANESE_TERMS['alert']} (ゼーレ):[/magenta] {synthesis['seele_alert']}

[b red]最終{JAPANESE_TERMS['directive']}: 多数決の{JAPANESE_TERMS['decision']}に従い、提示された留保事項と共に進行せよ。[/b red]
[b red]FINAL DIRECTIVE: Proceed according to majority decision, with presented reservations.[/b red]
"""
        self.console.print(Panel(
            content, 
            title=f"[bold red]碇ゲンドウ - 最終{JAPANESE_TERMS['directive']}[/bold red]", 
            border_style="red",
            width=self._get_responsive_width("wide")
        ))

    def display_shutdown(self):
        """Exibe shutdown com elementos japoneses."""
        self.console.print(f"\n[bold red]接続終了中... / Terminating Connection...[/bold red]")
        self.console.print(f"[dim]さようなら... / Sayonara...[/dim]")

    def display_error(self, message: str):
        """Exibe erro com texto sanitizado."""
        clean_message = self._sanitize_text(str(message))
        error_content = f"""
    [bold red]エラー / ERROR:[/bold red] {clean_message}
    [dim]{JAPANESE_TERMS['system']}障害が発生しました / System failure occurred[/dim]
    """
        self.console.print(Align.center(Panel(
            error_content, 
            title=f"[bold red]{JAPANESE_TERMS['system']}障害[/bold red]",
            width=self._get_responsive_width("normal")
        )))

    def clear_screen(self):
        """Limpa a tela e exibe um separador temático."""
        self.console.clear()
        self.console.print(Rule(f"ターミナルドグマ - {JAPANESE_TERMS['system']}リセット", style="red"))
        
    def display_at_field_interference(self, agent_name: str):
        """Exibe interferência no Campo AT."""
        
        # Mensagens aleatórias temáticas
        interference_messages = [
            "A.T.フィールド干渉を検出",
            "同期率が限界値に達しました", 
            "エントリープラグが応答しません",
            "LCL濃度が不安定です",
            "神経接続にノイズが発生"
        ]
        
        english_messages = [
            "A.T. Field interference detected",
            "Synchronization rate reached critical limit",
            "Entry plug not responding", 
            "L.C.L. concentration unstable",
            "Neural connection noise detected"
        ]
        
        jp_msg = random.choice(interference_messages)
        en_msg = random.choice(english_messages)
        
        # Mapear agentes para nomes japoneses
        agent_mapping = {
            "MELCHIOR-01": "メルキオール-01",
            "BALTHASAR-02": "バルタザール-02",
            "CASPER-03": "カスパー-03",
            "SEELE_INTERJECTOR": "ゼーレ",
            "ADAM_CATALYST": "アダム",
            "LILITH_FOUNDATION": "リリス",
            "LONGINUS_VETO": "ロンギヌス"
        }
        
        jp_agent = agent_mapping.get(agent_name, agent_name)
        
        content = f"""
    [bold red]⚠️  緊急事態発生  ⚠️[/bold red]
    [bold red]⚠️  EMERGENCY DETECTED  ⚠️[/bold red]

    [bold yellow]{jp_msg}[/bold yellow]
    [dim]{en_msg}[/dim]

    影響を受けたユニット / Affected Unit: [cyan]{jp_agent}[/cyan]

    [bold magenta]対処法:[/bold magenta]
    - システム管理者に連絡してください
    - しばらく時間をおいて再試行してください  
    - 別のエージェントを使用してください

    [bold magenta]Countermeasures:[/bold magenta]
    - Contact system administrator
    - Wait and retry after some time
    - Try using a different agent

    [dim]エラーコード: AT-FIELD-001[/dim]
    """
        
        # Efeito de "interferência" com bordas piscantes
        border_colors = ["red", "yellow", "magenta"]
        border_color = random.choice(border_colors)
        
        self.console.print(Panel(
            content,
            title=f"[bold {border_color}]A.T.フィールド干渉 - {jp_agent}[/bold {border_color}]",
            border_style=border_color,
            width=self._get_responsive_width("normal")
        ))

    def display_central_dogma_lockdown(self, subsystem: str):
        """Exibe lockdown do Central Dogma."""
        
        lockdown_reasons = [
            "定期メンテナンス実行中",
            "システム最適化処理中", 
            "セキュリティアップデート中",
            "データベース再構築中",
            "バックアップ処理実行中"
        ]
        
        english_reasons = [
            "Routine maintenance in progress",
            "System optimization in progress",
            "Security update in progress", 
            "Database reconstruction in progress",
            "Backup process in progress"
        ]
        
        jp_reason = random.choice(lockdown_reasons)
        en_reason = random.choice(english_reasons)
        
        content = f"""
    [bold red]🔒  セントラルドグマ封鎖  🔒[/bold red]
    [bold red]🔒  CENTRAL DOGMA LOCKDOWN  🔒[/bold red]

    理由 / Reason: [yellow]{jp_reason}[/yellow]
    [dim]{en_reason}[/dim]

    影響サブシステム / Affected Subsystem: [cyan]{subsystem}[/cyan]

    [bold blue]予想復旧時間 / Estimated Recovery:[/bold blue]
    15-30分 / 15-30 minutes

    [bold green]代替手段 / Alternatives:[/bold green]
    - 他のMAGIユニットを試してください
    - Try other MAGI units
    - しばらく待ってから再試行
    - Wait and retry later

    [dim]メンテナンスコード: DOGMA-MAINT-{random.randint(100,999)}[/dim]
    """

        self.console.print(Panel(
            content,
            title="[bold red]システムメンテナンス / SYSTEM MAINTENANCE[/bold red]",
            border_style="red",
            width=self._get_responsive_width("normal")
        ))

    def display_error(self, message: str):
        """Exibe erro com texto sanitizado."""
        clean_message = self._sanitize_text(str(message))
        error_content = f"""
    [bold red]エラー / ERROR:[/bold red] {clean_message}
    [dim]{JAPANESE_TERMS['system']}障害が発生しました / System failure occurred[/dim]
    """
        self.console.print(Align.center(Panel(
            error_content, 
            title=f"[bold red]{JAPANESE_TERMS['system']}障害[/bold red]",
            width=self._get_responsive_width("normal")
        )))
    
