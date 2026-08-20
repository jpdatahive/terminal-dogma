# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [Não lançado] — branch `feat/v2-rewrite`

Reescrita completa do projeto (v2): arquitetura hexagonal-lite, camada de LLM
provider-agnóstica, TUI com Textual, TDD em todas as fases.

### Adicionado

- **Fase 0 — Fundação**: uv + hatchling com src layout; entry point `dogma`; ruff,
  mypy strict, pytest, coverage, hypothesis, time-machine; CI com matriz Python
  3.11–3.13 e piso de cobertura de 85%; AGENTS.md; hooks de pre-commit.
- **Fase 1 — Domínio e parser**: enums de veredito (tokens PT-BR do contrato v1),
  modelos Pydantic imutáveis, exceções temáticas; parser puro e tolerante por tipo de
  agente com golden files e testes de propriedade (hypothesis).
- **Fase 2 — Estado unificado**: `DogmaState` (schema v2) substituindo os dois JSONs da
  v1; `JsonStateStore` com escrita atômica; `ParadigmCooldownService` (maturação de 100
  dias, cooldown, penalidade, chave horária MD5) com `Clock` injetável; migração
  tolerante dos arquivos v1.
- **Fase 3 — Camada LLM**: Protocol `LLMClient` assíncrono; `FakeLLMClient` scriptado;
  `ResilientLLMClient` (timeout + retry com backoff, sleep injetável); `GeminiClient`
  com SDK oficial (extra opcional) e tradução de erros tipados para exceções de domínio.
- **Fase 4 — Agentes**: `AgentSpec` (id, nome, cor, contrato de veredito, template) +
  7 prompts versionados em `agents/prompts/*.md` portados da v1 (regras do Longinus
  embutidas no próprio template); `Agent.analyze` (render → LLM → parse) com testes de
- **Fase 5 — Serviços de orquestração**: `MagiCouncil` (deliberação tripartite paralela com `asyncio.gather`), `LonginusVetoService` (circuit breaker e registro de violações), `SeeleMonitor` (vigilância em background e análise explícita), `ParadigmService` (simulação ADAM vs. LILITH com trava de maturação e chave horária), `DialectService` (debate dialético em turnos), `StatusService` e `DossierService`.
- **Fase 6 — TUI com Textual**: `DogmaApp` com interface assíncrona, widgets temáticos (`MagiDeliberationWidget`, `SeeleWidget`, `ParadigmWidget`, `VetoWidget`, `DialectWidget`, `DossierWidget`, `StatusWidget`, `StatusBar`, `HeaderWidget`, `HelpWidget`), histórico de deliberações e suíte de testes com Textual Pilot.
- **Fase 7 — Release e Documentação**: `README.md` atualizado, auto-migração de arquivos v1 ao inicializar, 201 testes (>99% de cobertura) e conformidade completa com a especificação v2.
- Documentação: README reescrito, `docs/ARCHITECTURE.md`, `docs/TESTING.md`,
  `docs/CONTRIBUTING.md` e ADRs 0001–0004.

### Corrigido (em relação à v1)

- Colisão de arquivo temporário entre escritores concorrentes no store de estado.
- Detecção de erros por string matching (substituída por exceções de domínio tipadas).
- "Senha" do Paradigm que era apenas o relógio (HH-MM-DD) — permanece a chave MD5
  horária.
- `__pycache__` removido do tracking do git.

### Descontinuado

- Dependência do LangChain (a camada `llm` usa Protocol próprio + SDK oficial).
- `requirements.txt` como fonte de dependências (substituído por `pyproject.toml` +
  `uv.lock`).
