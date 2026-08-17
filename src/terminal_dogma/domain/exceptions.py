"""Exceções temáticas do Terminal Dogma.

A camada ``llm`` traduz erros tipados dos SDKs para estas exceções;
nunca por string matching em mensagens de erro.
"""


class DogmaSystemException(Exception):
    """Exceção base para o sistema Terminal Dogma."""


class ATFieldInterference(DogmaSystemException):
    """Interferência no Campo AT — quota/rate limit do provedor de LLM."""

    def __init__(self, agent_name: str = "UNKNOWN") -> None:
        self.agent_name = agent_name
        super().__init__(f"A.T. Field interference detected in {agent_name}")


class CentralDogmaLockdown(DogmaSystemException):
    """Central Dogma em lockdown — falha de conexão/infraestrutura do provedor."""

    def __init__(self, subsystem: str = "MAGI") -> None:
        self.subsystem = subsystem
        super().__init__(f"Central Dogma lockdown initiated - {subsystem} under maintenance")


class AngelPatternDetected(DogmaSystemException):
    """Padrão Angel detectado — sistema em modo de emergência."""

    def __init__(self, message: str = "Unknown Angel pattern") -> None:
        super().__init__(f"Angel pattern detected: {message}")
