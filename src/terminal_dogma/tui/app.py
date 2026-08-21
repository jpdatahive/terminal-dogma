"""Aplicação principal da TUI com Textual para o Terminal Dogma."""

import os
from pathlib import Path

from textual import events
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Input

from terminal_dogma.domain.exceptions import DogmaSystemException
from terminal_dogma.domain.models import (
    MagiDeliberation,
    ParadigmExecution,
    SeeleReport,
    VetoResult,
)
from terminal_dogma.llm.base import LLMClient
from terminal_dogma.llm.fake import FakeLLMClient
from terminal_dogma.services.dialect import DialectService
from terminal_dogma.services.dossier import DossierService
from terminal_dogma.services.magi import MagiCouncil
from terminal_dogma.services.paradigm import ParadigmService
from terminal_dogma.services.seele import SeeleMonitor
from terminal_dogma.services.status import StatusService
from terminal_dogma.services.veto import LonginusVetoService
from terminal_dogma.state.clock import Clock, SystemClock
from terminal_dogma.state.cooldown import ParadigmCooldownService
from terminal_dogma.state.store import JsonStateStore, StateStore
from terminal_dogma.tui.widgets import (
    DialectWidget,
    DossierWidget,
    ErrorWidget,
    HeaderWidget,
    HelpWidget,
    MagiDeliberationWidget,
    ParadigmWidget,
    ProcessingWidget,
    SeeleWidget,
    StatusBar,
    StatusWidget,
    VetoWidget,
)


def _default_client() -> LLMClient:
    """Instancia o cliente padrão conforme variáveis de ambiente."""
    provider = os.environ.get("LLM_PROVIDER", "").lower()

    if provider == "ollama" or os.environ.get("OLLAMA_MODEL") or os.environ.get("OLLAMA_HOST"):
        from terminal_dogma.llm.ollama import OllamaClient
        from terminal_dogma.llm.resilient import ResilientLLMClient

        return ResilientLLMClient(OllamaClient.from_env())

    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        try:
            from terminal_dogma.llm.gemini import GeminiClient
            from terminal_dogma.llm.resilient import ResilientLLMClient

            return ResilientLLMClient(GeminiClient(api_key=api_key))
        except ImportError:
            pass
    return FakeLLMClient(
        default="NENHUM VETO\n\nAnálise padrão de demonstração offline.\nVOTO: POSITIVO"
    )


def _default_store() -> StateStore:
    """Cria ou localiza o store de persistência padrão, migrando v1 se necessário."""
    config_dir = Path.home() / ".config" / "terminal-dogma"
    config_dir.mkdir(parents=True, exist_ok=True)
    store_file = config_dir / "state.json"
    store = JsonStateStore(store_file)
    if not store_file.exists():
        reg = Path("dogma_registry.json")
        lock = Path("paradigm_lock.json")
        if reg.exists() or lock.exists():
            from terminal_dogma.state.migration import migrate_into

            migrate_into(store, reg if reg.exists() else None, lock if lock.exists() else None)
    return store


class DogmaApp(App[None]):
    """Aplicação TUI de deliberação do Terminal Dogma."""

    CSS = """
    Screen {
        background: #0d0e15;
        color: #e0e0e0;
    }
    #output-container {
        height: 1fr;
        padding: 1;
        overflow-y: auto;
    }
    #status-bar {
        height: auto;
        dock: bottom;
    }
    #cmd-input {
        dock: bottom;
        background: #151824;
        color: #00ffff;
        border: tall #ff0033;
    }
    """

    def __init__(
        self,
        council: MagiCouncil | None = None,
        seele: SeeleMonitor | None = None,
        paradigm: ParadigmService | None = None,
        veto: LonginusVetoService | None = None,
        dialect: DialectService | None = None,
        status_svc: StatusService | None = None,
        dossier_svc: DossierService | None = None,
        client: LLMClient | None = None,
        store: StateStore | None = None,
        clock: Clock | None = None,
        cooldown: ParadigmCooldownService | None = None,
    ) -> None:
        super().__init__()
        self._clock = clock or SystemClock()
        self._store = store or _default_store()
        self._client = client or _default_client()
        self._cooldown = cooldown or ParadigmCooldownService(self._store, self._clock)

        self._veto = veto or LonginusVetoService(self._client, self._store)
        self._council = council or MagiCouncil(self._client, self._store, veto_service=self._veto)
        self._seele = seele or SeeleMonitor(self._client, self._store)
        self._paradigm = paradigm or ParadigmService(
            self._client,
            self._store,
            self._clock,
            cooldown_service=self._cooldown,
            veto_service=self._veto,
        )
        self._dialect = dialect or DialectService(self._client)
        self._status_svc = status_svc or StatusService(
            self._store, self._clock, cooldown_service=self._cooldown
        )
        self._dossier_svc = dossier_svc or DossierService()

    def compose(self) -> ComposeResult:
        yield HeaderWidget()
        yield VerticalScroll(id="output-container")
        yield StatusBar(self._status_svc, id="status-bar")
        status = self._status_svc.get_status()
        yield Input(
            placeholder=f"DOGMA:{status.total_sessions + 1:03d}> Digite um comando...",
            id="cmd-input",
        )

    def on_mount(self) -> None:
        cmd_input = self.query_one(Input)
        cmd_input.focus()
        self.run_worker(self._mount_initial_help())

    async def _mount_initial_help(self) -> None:
        output = self.query_one("#output-container", VerticalScroll)
        await output.mount(HelpWidget())

    def on_key(self, event: events.Key) -> None:
        cmd_input = self.query_one(Input)
        if not cmd_input.has_focus:
            cmd_input.focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        raw_text = event.value.strip()
        cmd_input = self.query_one(Input)
        cmd_input.value = ""

        if not raw_text:
            return

        parts = raw_text.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1].strip() if len(parts) > 1 else ""

        if command in ("exit", "quit", "sair"):
            self.exit()
            return

        if command == "clear":
            output = self.query_one("#output-container", VerticalScroll)
            await output.remove_children()
            return

        new_session = self._status_svc.increment_session()
        cmd_input.placeholder = f"DOGMA:{new_session + 1:03d}> Digite um comando..."

        status_bar = self.query_one(StatusBar)
        status_bar.refresh()

        output = self.query_one("#output-container", VerticalScroll)
        processing = ProcessingWidget(f"{command} {args}".strip())
        await output.mount(processing)
        output.scroll_end(animate=False)

        self.run_worker(self._dispatch_command(command, args, processing))

    async def _dispatch_command(
        self,
        command: str,
        args: str,
        processing: ProcessingWidget | None = None,
    ) -> None:
        output = self.query_one("#output-container", VerticalScroll)

        try:
            if command == "help":
                await output.mount(HelpWidget())

            elif command == "status":
                status = self._status_svc.get_status()
                await output.mount(StatusWidget(status))

            elif command == "dossier":
                if not args:
                    await output.mount(
                        ErrorWidget(
                            "O comando 'dossier' requer um id de agente. Ex: dossier melchior-01"
                        )
                    )
                else:
                    dossier = self._dossier_svc.get_dossier(args)
                    await output.mount(DossierWidget(dossier))

            elif command == "seele":
                if not args:
                    await output.mount(
                        ErrorWidget(
                            "O comando 'seele' requer uma consulta. Ex: seele Analisar risco"
                        )
                    )
                else:
                    seele_report: SeeleReport = await self._seele.analyze_explicit(args)
                    await output.mount(SeeleWidget(seele_report, is_intervention=False))

            elif command == "veto":
                if not args:
                    await output.mount(
                        ErrorWidget("O comando 'veto' requer uma consulta. Ex: veto Proposta X")
                    )
                else:
                    veto_res: VetoResult = await self._veto.check_veto(args)
                    await output.mount(VetoWidget(veto_res, query_text=args))

            elif command == "magi":
                if not args:
                    await output.mount(
                        ErrorWidget(
                            "O comando 'magi' requer uma consulta. Ex: magi Aprovar expansão"
                        )
                    )
                else:
                    seele_rep: SeeleReport = await self._seele.monitor(args)
                    if seele_rep.intervention:
                        await output.mount(SeeleWidget(seele_rep, is_intervention=True))

                    delib: MagiDeliberation = await self._council.deliberate(args)
                    await output.mount(MagiDeliberationWidget(delib))

            elif command == "paradigm":
                if not args:
                    await output.mount(
                        ErrorWidget(
                            "O comando 'paradigm' requer uma consulta. "
                            "Ex: paradigm <chave> <consulta>"
                        )
                    )
                else:
                    tokens = args.split(maxsplit=1)
                    has_hex_key = (
                        len(tokens) > 1
                        and len(tokens[0]) == 8
                        and all(c in "0123456789abcdefABCDEF" for c in tokens[0])
                    )
                    key = tokens[0] if has_hex_key else self._cooldown.current_key()
                    query = tokens[1] if has_hex_key else args
                    paradigm_res: ParadigmExecution = await self._paradigm.execute(
                        query=query, key=key
                    )
                    await output.mount(ParadigmWidget(paradigm_res))

            elif command == "dialect":
                d_parts = args.split(maxsplit=2)
                if len(d_parts) < 3:
                    await output.mount(
                        ErrorWidget(
                            "O comando 'dialect' requer dois agentes e a consulta. "
                            "Ex: dialect melchior-01 casper-03 'tema'"
                        )
                    )
                else:
                    agent_a, agent_b, d_query = d_parts[0], d_parts[1], d_parts[2]
                    debate = await self._dialect.debate(agent_a, agent_b, d_query)
                    await output.mount(DialectWidget(debate))

            else:
                await output.mount(
                    ErrorWidget(
                        f"Comando desconhecido: '{command}'. Digite 'help' para ver os comandos."
                    )
                )

        except (KeyError, ValueError, DogmaSystemException) as e:
            await output.mount(ErrorWidget(str(e)))
        except Exception as e:
            await output.mount(ErrorWidget(f"Erro inesperado no subsistema: {e}"))
        finally:
            if processing is not None:
                await processing.remove()

        status_bar = self.query_one(StatusBar)
        status_bar.refresh()
        output.scroll_end(animate=False)
