# AGENTS.md — Terminal Dogma

## Contexto

CLI temático de *Neon Genesis Evangelion*: um "sistema de deliberação" onde o usuário submete
consultas e recebe análises de agentes de IA com personalidades distintas (conselho MAGI, comitê
SEELE, veto Longinus, sistema Paradigm).

O projeto está em **reescrita v2** (branch `feat/v2-rewrite`): arquitetura hexagonal-lite,
camada de LLM provider-agnóstica, TUI com Textual, desenvolvimento orientado a testes (TDD).

## Estrutura

```
src/terminal_dogma/   # Pacote v2 (código novo — TODO trabalho acontece aqui)
src/dogma_core/       # Código v1 CONGELADO — referência apenas, não modificar, não lintar
tests/                # Suíte v2 (unit/, contract/, integration/, tui/, live/)
tests/legacy/         # Suíte v1 congelada (ignorada pelo pytest por padrão)
docs/                 # Documentação (ARCHITECTURE, TESTING, CONTRIBUTING, adr/)
```

Módulos planejados para a v2 (criados fase a fase):

- `domain/` — modelos Pydantic, enums de veredito, exceções temáticas (zero deps externas)
- `parsing/` — parser puro das saídas textuais dos agentes
- `state/` — StateStore unificado, serviço de cooldown, migração dos JSONs v1
- `llm/` — Protocol `LLMClient` + adaptadores (Gemini, OpenAI, Anthropic, Ollama, Fake)
- `agents/` — specs de agentes + templates de prompt versionados
- `services/` — orquestração (MagiCouncil, SeeleMonitor, ParadigmService, LonginusVeto, Dialect)
- `tui/` — app Textual (Fase 6)

## Comandos

```bash
uv sync                              # instala dependências (cria .venv)
uv run pytest                        # roda a suíte v2 (ignora tests/legacy)
uv run pytest --cov=src/terminal_dogma --cov-report=term-missing   # com cobertura
uv run ruff check . && uv run ruff format --check .                # lint + formato
uv run mypy                          # typecheck estrito do pacote v2
uv run dogma                         # entry point do CLI
```

CI (GitHub Actions) roda lint, formato, mypy e testes (Python 3.11–3.13) com cobertura
mínima de 85% em `src/terminal_dogma`.

## Convenções

- **TDD obrigatório**: teste que falha primeiro (red), depois implementação (green), refactor.
  Todo bug corrigido vira um teste de regressão.
- **Commits**: Conventional Commits em inglês (`feat:`, `fix:`, `test:`, `chore:`, `ci:`,
  `docs:`, `build:`), escopo opcional (`feat(parsing): ...`). Um commit por unidade lógica.
- **Idiomas**: código e identificadores em inglês; documentação, docstrings, UI e prompts
  dos agentes em PT-BR.
- **Regras de dependência**: `domain` não importa nada do projeto; `services` não importa
  `tui` nem SDKs de LLM; `tui` consome `services` por injeção de dependência; a camada `llm`
  traduz erros tipados dos SDKs para exceções de domínio (nunca string matching).
- **Legado v1**: não editar `src/dogma_core/` nem `tests/legacy/`; ambos excluídos de
  ruff/mypy/pytest via configuração.
- Qualidade exigida antes de commit: `pytest`, `ruff check`, `ruff format --check` e `mypy`
  todos verdes.
