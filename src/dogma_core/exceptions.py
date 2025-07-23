class DogmaSystemException(Exception):
    """Exceção base para o sistema Terminal Dogma."""
    pass

class ATFieldInterference(DogmaSystemException):
    """Interferência no Campo AT detectada - equivale a erros de quota/rate limit."""
    def __init__(self, agent_name: str = "UNKNOWN"):
        self.agent_name = agent_name
        super().__init__(f"A.T. Field interference detected in {agent_name}")

class AngelPatternDetected(DogmaSystemException):
    """Padrão Angel detectado - sistema em modo de emergência."""
    def __init__(self, message: str = "Unknown Angel pattern"):
        super().__init__(f"Angel pattern detected: {message}")

class CentralDogmaLockdown(DogmaSystemException):
    """Central Dogma em lockdown - manutenção crítica."""
    def __init__(self, subsystem: str = "MAGI"):
        self.subsystem = subsystem
        super().__init__(f"Central Dogma lockdown initiated - {subsystem} under maintenance")