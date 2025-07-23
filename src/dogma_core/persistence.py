import json
import os
from datetime import datetime, timedelta
import hashlib

class DogmaRegistry:
    """
    Sistema de persistência para o Terminal Dogma.
    Gerencia timestamps, contadores de uso e validações temporais.
    """
    
    def __init__(self, registry_file="dogma_registry.json"):
        self.registry_file = registry_file
        self.registry = self._load_registry()
        
    def _load_registry(self) -> dict:
        """Carrega o registro do disco ou cria um novo."""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Registro inicial
        initial_registry = {
            "first_boot": datetime.now().isoformat(),
            "last_paradigm_use": None,
            "paradigm_uses": 0,
            "seele_interventions": 0,
            "longinus_activations": 0,
            "total_sessions": 0
        }
        self._save_registry(initial_registry)
        return initial_registry
    
    def _save_registry(self, data: dict = None):
        """Salva o registro no disco."""
        data = data or self.registry
        with open(self.registry_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_days_since_first_boot(self) -> int:
        """Retorna quantos dias se passaram desde o primeiro boot."""
        first_boot = datetime.fromisoformat(self.registry["first_boot"])
        return (datetime.now() - first_boot).days
    
    def can_use_paradigm(self) -> bool:
        """Verifica se os agentes de paradigma podem ser usados."""
        days_since_boot = self.get_days_since_first_boot()
        
        # Não pode usar antes de 100 dias
        if days_since_boot < 100:
            return False
            
        # Se nunca foi usado, pode usar
        if not self.registry["last_paradigm_use"]:
            return True
            
        # Verifica se passaram 100 dias desde o último uso
        last_use = datetime.fromisoformat(self.registry["last_paradigm_use"])
        days_since_last_use = (datetime.now() - last_use).days
        return days_since_last_use >= 100
    
    def generate_paradigm_key(self) -> str:
        """Gera a chave baseada na hora atual para usar os agentes de paradigma."""
        now = datetime.now()
        seed = f"{now.year}{now.month:02d}{now.day:02d}{now.hour:02d}"
        return hashlib.md5(seed.encode()).hexdigest()[:8].upper()
    
    def validate_paradigm_key(self, provided_key: str) -> bool:
        """Valida se a chave fornecida está correta."""
        return provided_key.upper() == self.generate_paradigm_key()
    
    def register_paradigm_use(self):
        """Registra o uso dos agentes de paradigma."""
        self.registry["last_paradigm_use"] = datetime.now().isoformat()
        self.registry["paradigm_uses"] += 1
        self._save_registry()
    
    def register_seele_intervention(self):
        """Registra uma intervenção do SEELE."""
        self.registry["seele_interventions"] += 1
        self._save_registry()
    
    def register_longinus_activation(self):
        """Registra uma ativação do Longinus."""
        self.registry["longinus_activations"] += 1
        self._save_registry()
    
    def reset_progress(self):
        """Reseta o progresso quando Longinus é ativado."""
        self.registry["last_paradigm_use"] = None
        self.registry["paradigm_uses"] = 0
        self._save_registry()
    
    def increment_session(self):
        """Incrementa o contador de sessões."""
        self.registry["total_sessions"] += 1
        self._save_registry()
    
    def get_status(self) -> dict:
        """Retorna informações de status para exibição."""
        days_since_boot = self.get_days_since_first_boot()
        can_paradigm = self.can_use_paradigm()
        
        days_until_paradigm = None
        if not can_paradigm:
            if not self.registry["last_paradigm_use"]:
                days_until_paradigm = 100 - days_since_boot
            else:
                last_use = datetime.fromisoformat(self.registry["last_paradigm_use"])
                days_since_last_use = (datetime.now() - last_use).days
                days_until_paradigm = 100 - days_since_last_use
        
        return {
            "days_since_boot": days_since_boot,
            "can_use_paradigm": can_paradigm,
            "days_until_paradigm": max(0, days_until_paradigm) if days_until_paradigm else 0,
            "paradigm_uses": self.registry["paradigm_uses"],
            "seele_interventions": self.registry["seele_interventions"],
            "longinus_activations": self.registry["longinus_activations"],
            "total_sessions": self.registry["total_sessions"]
        }