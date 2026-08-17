"""Especificações estáticas dos agentes (dados, não comportamento)."""

from dataclasses import dataclass
from functools import cache
from importlib.resources import files

from terminal_dogma.domain.verdicts import VerdictKind

#: Marcador no template de prompt substituído pela consulta do usuário.
QUERY_PLACEHOLDER = "{query}"


@cache
def _read_prompt(filename: str) -> str:
    return (
        files("terminal_dogma.agents")
        .joinpath("prompts")
        .joinpath(filename)
        .read_text(encoding="utf-8")
    )


@dataclass(frozen=True)
class AgentSpec:
    """Identidade, apresentação e contrato de saída de um agente."""

    id: str
    name: str
    color: str
    verdict: VerdictKind
    prompt_file: str

    def load_prompt(self) -> str:
        """Carrega o template de prompt versionado (cacheado)."""
        return _read_prompt(self.prompt_file)
