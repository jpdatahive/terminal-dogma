# Contribuindo — Terminal Dogma

## Setup

```bash
git clone https://github.com/jpdatahive/terminal-dogma.git
cd terminal-dogma
git checkout feat/v2-rewrite
uv sync
pre-commit install   # opcional, mas recomendado
```

## Gates de qualidade (obrigatórios antes de commit)

```bash
uv run pytest                # testes
uv run ruff check .          # lint
uv run ruff format --check . # formato
uv run mypy                  # typecheck estrito (src/terminal_dogma)
```

O CI roda os mesmos gates em Python 3.11, 3.12 e 3.13, com cobertura mínima de 85%.

## Fluxo de trabalho

1. Trabalhe no branch `feat/v2-rewrite` (ou branches de feature derivados dele).
2. Siga TDD: commit `test:` com o teste falhando, depois `feat:` com a implementação.
3. Um commit por unidade lógica.

## Convenções

- **Commits**: Conventional Commits em inglês (`feat:`, `fix:`, `test:`, `chore:`,
  `ci:`, `docs:`, `build:`), escopo opcional — ex.: `feat(parsing): ...`.
- **Idiomas**: código e identificadores em inglês; documentação, docstrings, UI e
  prompts de agentes em PT-BR.
- **Legado v1**: nunca editar `src/dogma_core/` nem `tests/legacy/` — são referência
  congelada, excluídos de ruff/mypy/pytest via configuração.
- **Regras de dependência**: ver `docs/ARCHITECTURE.md`. Em resumo: `domain` no centro;
  `services` sem imports de `tui`/SDKs; `llm` traduz erros tipados para exceções de
  domínio (nunca string matching).

## Adicionando um novo provedor de LLM (a partir da Fase 3)

1. Crie `src/terminal_dogma/llm/<provider>.py` implementando `LLMClient`
   (`async complete(prompt) -> str`), com import do SDK feito de forma lazy.
2. Traduza os erros tipados do SDK para `ATFieldInterference` / `CentralDogmaLockdown`.
3. Registre o SDK como extra opcional em `pyproject.toml`.
4. Adicione testes unitários com o client mockado e um teste `live` com `skipif`.
