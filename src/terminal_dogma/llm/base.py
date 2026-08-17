"""Contrato da camada de LLM (provider-agnóstico)."""

from typing import Protocol


class LLMClient(Protocol):
    """Cliente de LLM assíncrono usado por todos os agentes e serviços."""

    async def complete(self, prompt: str) -> str:
        """Envia o prompt e retorna o texto da resposta.

        Erros do provedor chegam aos chamadores já traduzidos para exceções
        de domínio (``ATFieldInterference`` para rate limit/quota,
        ``CentralDogmaLockdown`` para falhas de conexão/infra).
        """
        ...
