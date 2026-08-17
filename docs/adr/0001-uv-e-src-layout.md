# ADR 0001 — uv + src layout

- **Status**: Aceito (implementado na Fase 0)
- **Data**: 2026-08-16

## Contexto

A v1 tinha `pyproject.toml` vazio, `requirements.txt` sem versões pinadas, pacote
não instalável e testes com hack de `sys.path`.

## Decisão

Adotar **uv** como gerenciador de pacotes/ambientes (com `uv.lock` versionado) e
**src layout** com hatchling como build backend. O pacote v2 é `terminal_dogma`
(`src/terminal_dogma/`), instalado em modo editável por `uv sync`, com entry point
`dogma`. Ferramentas (ruff, mypy, pytest, coverage) configuradas no `pyproject.toml`;
dependências de desenvolvimento em `[dependency-groups]`.

## Consequências

- Builds reproduzíveis (lockfile) e setup de um comando (`uv sync`).
- Imports nos testes sem hacks de path (pacote instalado).
- `src/dogma_core/` (v1) convive no repositório, fora do build e do pipeline de
  qualidade (`extend-exclude`), como referência congelada.
- CI usa `astral-sh/setup-uv` e `uv sync --frozen`.
