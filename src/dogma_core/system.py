# system.py -> Adicione estas importações no início do arquivo
import sys
import time
import re
import json
from datetime import datetime, timedelta
from . import agents
from . import ui
from rich.panel import Panel
import random


# system.py -> Substitua a classe DogmaSystem inteira pela versão abaixo

class DogmaSystem:
    """
    A classe principal que orquestra o Terminal Dogma como um centro de comando.
    Gerencia múltiplos sistemas de deliberação (MAGI, SEELE, etc.) e despacha os comandos.
    """
    LOCK_FILE = "paradigm_lock.json"
    PARADIGM_COOLDOWN_DAYS = 100

    def __init__(self):
        """
        Inicializa o sistema, o controlador da UI e todos os agentes necessários.
        """
        self.ui = ui.UIController()
        self._initialize_state()
        try:
            # Os agentes agora são armazenados individualmente para chamadas específicas
            self.melchior = agents.MelchiorAgent()
            self.balthasar = agents.BalthasarAgent()
            self.casper = agents.CasperAgent()
            self.adam = agents.AdamAgent()
            self.lilith = agents.LilithAgent()
            self.seele = agents.SeeleAgent()
            self.longinus = agents.LonginusAgent()
        except RuntimeError as e:
            self.ui.display_error(f"Falha na inicialização do sistema: {e}")
            sys.exit(1)
        self.session_count = 0

    def _initialize_state(self):
        """Verifica e inicializa o arquivo de estado do sistema."""
        try:
            with open(self.LOCK_FILE, 'r') as f:
                state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Arquivo não existe ou está corrompido, cria um novo
            state = {
                "project_creation_timestamp": datetime.now().isoformat(),
                "last_paradigm_usage_timestamp": None
            }
            self._save_state(state)
        self.system_state = state

    def _save_state(self, state):
        """Salva o estado atual no arquivo JSON."""
        with open(self.LOCK_FILE, 'w') as f:
            json.dump(state, f, indent=4)
        self.system_state = state

    def _parse_analysis(self, full_text: str, default_verdict_key="verdict") -> dict:
        """
        Método auxiliar para extrair a análise e o veredito do texto de um agente.
        """
        match = re.search(r"(VOTO|ALERTA DE RISCO|POTENCIAL|ALINHAMENTO|VETO ACIONADO|NENHUM VETO|ALERTA):\s*(.*)", full_text, re.IGNORECASE | re.DOTALL)
        if not match:
            return {"analysis": full_text, default_verdict_key: "INDETERMINADO"}
        
        verdict = match.group(0).strip()
        analysis_text = full_text[:match.start()].strip()
        
        # Tratamento especial para o novo formato do SEELE
        if "INTERVENÇÃO:" in full_text:
            intervention_match = re.search(r"INTERVENÇÃO:\s*(SIM|NÃO)", full_text, re.IGNORECASE)
            analysis_match = re.search(r"ANÁLISE:\s*(.*)", full_text, re.DOTALL | re.IGNORECASE)
            alert_match = re.search(r"ALERTA:\s*(.*)", full_text, re.IGNORECASE)
            
            return {
                "intervention": intervention_match.group(1).upper() if intervention_match else "NÃO",
                "analysis": analysis_match.group(1).strip().split("ALERTA:")[0].strip() if analysis_match else "Análise não extraída.",
                "verdict": alert_match.group(1).strip() if alert_match else "Alerta não especificado."
            }

        return {"analysis": analysis_text, default_verdict_key: verdict}

    def _check_seele_intervention(self, query: str):
        """Verifica silenciosamente com o SEELE se uma intervenção é necessária."""
        with self.ui.console.status("[dim]Monitorando canais da SEELE...[/dim]", spinner="point"):
             # Adiciona um pequeno delay para a imersão de que algo está acontecendo em background
            time.sleep(random.uniform(0.5, 1.5))
            analysis_text = self.seele.analyze(query)
        result = self._parse_analysis(analysis_text)
        
        if result.get("intervention") == "SIM":
            self.ui.display_seele_report(result, is_intervention=True)
            time.sleep(2) # Pausa para o usuário ler o alerta

    def run(self):
        """
        O loop principal da aplicação. Funciona como um despachante de comandos.
        """
        self.ui.display_boot_sequence()
        while True:
            try:
                raw_input = self.ui.get_user_input(self.session_count)
                if not raw_input.strip():
                    continue

                parts = raw_input.strip().split(maxsplit=1)
                command = parts[0].lower()
                query = parts[1] if len(parts) > 1 else ""

                # --- LÓGICA DE INTERVENÇÃO DO SEELE ---
                # SEELE analisa TUDO, exceto comandos de sistema.
                if command not in ["help", "status", "clear", "exit", "quit", "sair"]:
                    self._check_seele_intervention(query or command)

                self.session_count += 1

                if command == "magi":
                    self._execute_magi_deliberation(query)
                elif command == "seele":
                    # Comando explícito ainda funciona, mas agora é marcado como uma análise solicitada
                    self._execute_seele_analysis(query)
                elif command == "paradigm":
                    self._execute_paradigm_analysis(query)
                elif command == "veto":
                    self._execute_longinus_veto(query)
                # O comando 'gendo' foi removido para manter a lógica mais simples com as novas regras,
                # mas pode ser readicionado se necessário.
                elif command == "help":
                    self.ui.display_help()
                elif command == "status":
                    self.ui.display_status()
                elif command == "clear":
                    self.ui.clear_screen()
                elif command in ["exit", "quit", "sair"]:
                    self.ui.display_shutdown()
                    sys.exit(0)
                else:
                    self.ui.display_error(f"Comando desconhecido: '{command}'. Digite 'help' para a lista de comandos.")

            except KeyboardInterrupt:
                self.ui.display_shutdown()
                sys.exit(0)
            except Exception as e:
                self.ui.display_error(f"Ocorreu um erro inesperado: {e}")


    def _execute_magi_deliberation(self, query: str):
        """
        Executa a deliberação do MAGI, mas somente após a verificação do Longinus.
        """
        self.ui.display_system_header("MAGI")
        if not query: self.ui.display_error("O comando 'magi' requer uma consulta."); return

        # --- VETO ABSOLUTO DA LONGINUS ---
        with self.ui.console.status("[bold red]Verificando protocolos de veto...[/bold red]"):
            veto_text = self.longinus.analyze(query)
            veto_result = self._parse_analysis(veto_text)
        
        if "VETO ACIONADO" in veto_result['verdict']:
            self.ui.display_longinus_veto(veto_result)
            self.ui.display_error("DELIBERAÇÃO MAGI CANCELADA DEVIDO AO VETO DA LONGINUS.")
            return

        self.ui.display_longinus_veto(veto_result) # Mostra que o veto foi checado e passou

        results = {}
        for agent in [self.melchior, self.balthasar, self.casper]:
            with self.ui.console.status(f"[bold]Consultando {agent.name}...[/bold]"):
                analysis_text = agent.analyze(query)
                results[agent.name] = self._parse_analysis(analysis_text)
            self.ui.display_agent_analysis(agent.name, results[agent.name])
        
        votes = [res['verdict'] for res in results.values()]
        positivos = sum('POSITIVO' in v for v in votes)
        negativos = len(votes) - positivos
        self.ui.display_magi_decision(positivos, negativos)

    def _execute_seele_analysis(self, query: str):
        """ Executa a análise de risco do comitê SEELE explicitamente. """
        self.ui.display_system_header("SEELE")
        if not query: self.ui.display_error("O comando 'seele' requer uma consulta."); return

        with self.ui.console.status(f"[bold magenta]Analisando vetores de ataque...[/bold magenta]"):
            analysis_text = self.seele.analyze(query)
            # Reutiliza o parser, mas ignora a parte de "intervenção"
            parsed_text = re.sub(r"INTERVENÇÃO:\s*(SIM|NÃO)\s*\n?", "", analysis_text, flags=re.IGNORECASE)
            result = self._parse_analysis(parsed_text)
        self.ui.display_seele_report(result, is_intervention=False)

    def _check_paradigm_availability(self):
        """Verifica se o sistema PARADIGM pode ser usado."""
        now = datetime.now()
        creation_time = datetime.fromisoformat(self.system_state["project_creation_timestamp"])
        
        # Checagem 1: Já se passaram 100 dias desde a criação do projeto?
        if (now - creation_time) < timedelta(days=self.PARADIGM_COOLDOWN_DAYS):
            return False, f"Acesso negado. O sistema Progenitor requer {self.PARADIGM_COOLDOWN_DAYS} dias de maturação após a inicialização."

        # Checagem 2: Se já foi usado, já se passaram 100 dias desde o último uso?
        last_usage = self.system_state.get("last_paradigm_usage_timestamp")
        if last_usage:
            last_usage_time = datetime.fromisoformat(last_usage)
            if (now - last_usage_time) < timedelta(days=self.PARADIGM_COOLDOWN_DAYS):
                return False, f"Acesso negado. O sistema está em cooldown por mais {(last_usage_time + timedelta(days=self.PARADIGM_COOLDOWN_DAYS) - now).days} dias."
        
        return True, "Sistema Paradigm pronto para ativação."

    def _generate_paradigm_password(self):
        """Gera a senha do dia no formato HH-MM-DD."""
        return datetime.now().strftime("%H-%M-%d")

    def _execute_paradigm_analysis(self, full_input: str):
        """
        Executa a análise de paradigma, com travas de tempo e senha.
        O uso indevido aciona o veto da Longinus e reinicia o contador.
        """
        self.ui.display_system_header("PARADIGM")
        is_available, message = self._check_paradigm_availability()

        if not is_available:
            self.ui.display_error(f"FALHA NO ACESSO AO PARADIGM: {message}")
            
            # --- CONSEQUÊNCIA DO VETO LONGINUS ---
            self.ui.display_system_header("LONGINUS")
            veto_query = "Tentativa de uso do sistema Paradigm fora do protocolo de tempo."
            veto_text = self.longinus.analyze(veto_query)
            veto_result = self._parse_analysis(veto_text)
            self.ui.display_longinus_veto(veto_result)
            self.ui.display_error("Penalidade acionada: O cronômetro de resfriamento do sistema Paradigm foi reiniciado.")
            
            # Reinicia o contador como penalidade
            self.system_state["last_paradigm_usage_timestamp"] = datetime.now().isoformat()
            self._save_state(self.system_state)
            return

        # Separa a senha da consulta
        parts = full_input.split(maxsplit=1)
        password = parts[0]
        query = parts[1] if len(parts) > 1 else ""
        expected_password = self._generate_paradigm_password()
        
        if not query:
            self.ui.display_error("O comando 'paradigm' requer uma senha e uma consulta. Formato: paradigm <senha> <consulta>"); return
        
        if password != expected_password:
            self.ui.display_error(f"Senha de autorização incorreta. A senha para a hora atual é gerada no formato HH-MM-DD (ex: {expected_password}). Tente novamente no próximo minuto se necessário."); return

        # Se tudo estiver correto, procede com a análise
        with self.ui.console.status(f"[bold cyan]Avaliando potencial disruptivo (ADAM)...[/bold cyan]"):
            adam_text = self.adam.analyze(query)
            adam_result = self._parse_analysis(adam_text)

        with self.ui.console.status(f"[bold white]Avaliando impacto fundamental (LILITH)...[/bold white]"):
            lilith_text = self.lilith.analyze(query)
            lilith_result = self._parse_analysis(lilith_text)

        self.ui.display_paradigm_comparison(adam_result, lilith_result)

        # --- CONSEQUÊNCIA DO USO: ATUALIZA O TIMESTAMP ---
        self.ui.console.print(Panel("[bold yellow]CONSEQUÊNCIA: O uso do sistema Paradigm iniciou um novo ciclo de resfriamento de 100 dias.", title="[bold red]ALERTA DE SISTEMA[/bold red]"))
        self.system_state["last_paradigm_usage_timestamp"] = datetime.now().isoformat()
        self._save_state(self.system_state)

    def _execute_longinus_veto(self, query: str):
        """ Verifica uma proposta contra as regras de veto da Lança de Longinus. """
        self.ui.display_system_header("LONGINUS")
        if not query: self.ui.display_error("O comando 'veto' requer uma consulta."); return

        with self.ui.console.status(f"[bold red]Verificando violações de protocolo...[/bold red]"):
            veto_text = self.longinus.analyze(query)
            veto_result = self._parse_analysis(veto_text)
        self.ui.display_longinus_veto(veto_result)

    # O método _execute_gendo_synthesis foi removido para simplificar, 
    # pois sua lógica original entra em conflito com as novas regras de veto e cooldown.