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

> **Status:** reescrita completa (v2) concluída — arquitetura hexagonal-lite,
> camada de LLM provider-agnóstica, TUI reativa com Textual e desenvolvimento orientado a testes (100% TDD).

## Roadmap da v2

| Fase | Entrega | Status |
|------|---------|--------|
| 0 | Fundação: uv, src layout, CI, AGENTS.md | ✅ concluída |
| 1 | Domínio (vereditos, modelos, exceções) + parser tolerante | ✅ concluída |
| 2 | Estado unificado (store atômico, cooldown, migração v1) | ✅ concluída |
| 3 | Camada LLM provider-agnóstica (Protocol, Fake, Resilient, Gemini) | ✅ concluída |
| 4 | Agentes: specs + templates de prompt versionados | ✅ concluída |
| 5 | Serviços de orquestração (MAGI paralelo, SEELE, Paradigm, Dialect, Status, Dossier) | ✅ concluída |
| 6 | TUI com Textual (widgets reativos, command input, Textual Pilot) | ✅ concluída |
| 7 | Documentação final e release v2.0.0 | ✅ concluída |

Detalhes de design em [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) e nas
[ADRs](docs/adr/). Como contribuir: [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md).

## Execução e Desenvolvimento (v2)

Requisito: [uv](https://docs.astral.sh/uv/) e Python 3.11+.

```bash
git clone https://github.com/jpdatahive/terminal-dogma.git
cd terminal-dogma
uv sync                  # instala dependências e cria o ambiente virtual

# Opção A: Usar com Ollama (local e gratuito)
ollama serve &
export OLLAMA_MODEL="llama3.2"  # ou mistral, qwen2.5, etc.

# Opção B: Usar com Google Gemini
export GOOGLE_API_KEY="sua_chave_gemini"

# Iniciar a TUI do Terminal Dogma (sem variáveis, roda em modo demo com FakeLLM)
uv run dogma
```

### Comandos do Terminal Dogma (TUI)

- `magi <consulta>` — Deliberação tripartite MAGI (Melchior, Balthasar, Casper) com monitoramento SEELE em paralelo
- `seele <consulta>` — Análise de risco pessimista e conservadora do comitê SEELE
- `paradigm [<chave>] <consulta>` — Simulação Progenitora (ADAM vs. LILITH) com ciclo de resfriamento de 100 dias
- `veto <consulta>` — Verificação direta de regras invioláveis pela Lança de Longinus
- `dialect <agente1> <agente2> <consulta>` — Debate dialético em turnos entre duas unidades MAGI
- `dossier <agente_id>` — Consulta detalhada do perfil e diretriz central de um agente
- `status` — Relatório operacional, contadores e chave horária MD5
- `clear` — Limpa o histórico da tela
- `exit` / `quit` / `sair` — Encerra a aplicação

### Verificação de Qualidade e Testes

```bash
uv run pytest --cov=src/terminal_dogma --cov-report=term-missing   # 201 testes (>99% cobertura)
uv run ruff check . && uv run ruff format --check .                # linter e formato
uv run mypy                                                        # tipagem estrita
```

---

*Aviso: este é um projeto para fins de entretenimento e exploração de conceitos de IA. As
análises são geradas por modelos de linguagem e não devem ser consideradas conselhos
profissionais.*
