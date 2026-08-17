"""Agente concreto: spec + LLMClient."""

from terminal_dogma.agents.spec import AgentSpec
from terminal_dogma.domain.models import AnalysisResult
from terminal_dogma.llm.base import LLMClient


class Agent:
    """Executa a análise de um agente: renderiza o prompt, consulta o LLM
    e faz o parse da saída conforme o contrato da spec."""

    def __init__(self, spec: AgentSpec, client: LLMClient) -> None:
        self.spec = spec
        self._client = client

    @property
    def name(self) -> str:
        return self.spec.name

    async def analyze(self, query: str) -> AnalysisResult:
        raise NotImplementedError
