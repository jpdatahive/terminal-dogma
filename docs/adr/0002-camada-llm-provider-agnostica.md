# ADR 0002 — Camada LLM provider-agnóstica

- **Status**: Aceito (implementação na Fase 3)
- **Data**: 2026-08-16

## Contexto

A v1 acopla os agentes ao `langchain_google_genai`: cada agente instancia seu próprio
`ChatGoogleGenerativeAI`, o modelo (`gemini-1.5-flash`, descontinuado) é constante de
módulo, e erros são detectados por string matching em mensagens de exceção — frágil e
preso a um único provedor.

## Decisão

Criar `terminal_dogma.llm` com um **Protocol próprio** minimalista:

```python
class LLMClient(Protocol):
    async def complete(self, prompt: str) -> str: ...
```

- Adaptadores por provedor; **Gemini** usa o SDK oficial `google-genai` (sem LangChain),
  distribuído como **extra opcional** (`uv sync --extra gemini`).
- `FakeLLMClient` scriptado para toda a suíte de testes (sem rede).
- `ResilientLLMClient` (decorator) provê timeout + retry com backoff de forma
  provider-agnóstica, com sleep injetável.
- Erros **tipados** dos SDKs são traduzidos para exceções de domínio
  (`ATFieldInterference` = rate limit/quota; `CentralDogmaLockdown` = falha de
  conexão/infra). String matching é proibido.
- Nome do modelo, temperatura e chaves são configuração (pydantic-settings), não código.

## Consequências

- Agentes e serviços são testáveis sem rede nem chaves de API.
- Trocar de provedor/modelo é configuração, não refatoração.
- Menos uma dependência pesada (LangChain sai; entra o SDK oficial enxuto).
- Cada adaptador faz import lazy do seu SDK, para que a instalação base não exija
  nenhum provedor.
