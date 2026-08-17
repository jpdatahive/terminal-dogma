# Terminal Dogma

![CI](https://github.com/jpdatahive/terminal-dogma/actions/workflows/ci.yml/badge.svg?branch=feat/v2-rewrite)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Cobertura](https://img.shields.io/badge/cobertura-100%25-brightgreen)

**Um sistema de deliberação temático de Neon Genesis Evangelion, rodando no seu terminal.**

Submeta uma consulta (uma pergunta, um problema, uma ideia) e receba análises de agentes de IA
com personalidades e diretrizes distintas: o conselho **MAGI** (lógica, ética e pragmatismo em
votação), o comitê **SEELE** (análise de risco pessimista, monitorando tudo em background), a
**Lança de Longinus** (veto binário contra regras invioláveis) e o sistema **Paradigm**
(inovação vs. estabilidade, com cooldown de 100 dias).

> **Status:** o projeto está em reescrita completa (v2) no branch `feat/v2-rewrite` —
> arquitetura hexagonal-lite, camada de LLM provider-agnóstica, TUI com Textual e
> desenvolvimento orientado a testes. O código v1 permanece funcional em `src/dogma_core/`.

## Roadmap da v2

| Fase | Entrega | Status |
|------|---------|--------|
| 0 | Fundação: uv, src layout, CI, AGENTS.md | ✅ concluída |
| 1 | Domínio (vereditos, modelos, exceções) + parser tolerante | ✅ concluída |
| 2 | Estado unificado (store atômico, cooldown, migração v1) | ✅ concluída |
| 3 | Camada LLM provider-agnóstica (Protocol, Fake, Gemini) | 🚧 em andamento |
| 4 | Agentes: specs + templates de prompt versionados | planejada |
| 5 | Serviços de orquestração (MAGI paralelo, SEELE, Paradigm, Dialect) | planejada |
| 6 | TUI com Textual | planejada |
| 7 | Documentação final e release v2.0.0 | planejada |

Detalhes de design em [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) e nas
[ADRs](docs/adr/). Como contribuir: [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md).

## Desenvolvimento (v2)

Requisito: [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/jpdatahive/terminal-dogma.git
cd terminal-dogma
git checkout feat/v2-rewrite
uv sync                 # instala dependências e o pacote em modo editável

uv run pytest           # suíte v2 (76 testes, ignorando tests/legacy)
uv run ruff check .     # lint
uv run mypy             # typecheck estrito
uv run dogma            # entry point (banner placeholder até a Fase 6)
```

## Aplicação v1 (legada, funcional)

A v1 continua disponível enquanto a v2 é construída:

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo "GOOGLE_API_KEY=sua_chave" > .env
python -m src.dogma_core.main
```

Comandos da v1: `magi <consulta>`, `seele <consulta>`, `paradigm <senha> <consulta>`,
`veto <consulta>`, `dialect <agente1> <agente2> <consulta>`, `status`, `help`.

---

*Aviso: este é um projeto para fins de entretenimento e exploração de conceitos de IA. As
análises são geradas por modelos de linguagem e não devem ser consideradas conselhos
profissionais.*
