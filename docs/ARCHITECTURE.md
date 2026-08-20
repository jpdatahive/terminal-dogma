# Arquitetura — Terminal Dogma v2

## Visão geral

Arquitetura **hexagonal-lite**: o domínio fica no centro, sem depender de UI nem de SDKs de
LLM; os adaptadores ficam nas bordas. As setas indicam a direção permitida das importações:

```
┌─────────────────────────────────────────────────┐
│  tui/        Textual app (telas, widgets)       │  Fase 6
├─────────────────────────────────────────────────┤
│  services/   MagiCouncil, SeeleMonitor,         │  Fase 5
│              ParadigmService, LonginusVeto,     │
│              DialectService                     │
├──────────────┬──────────────┬───────────────────┤
│  agents/     │  parsing/    │  state/           │  Fases 1, 2 e 4
│  (specs +    │  (parser     │  (StateStore,     │
│   prompts)   │   puro)      │   cooldown, clock)│
├──────────────┴──────────────┴───────────────────┤
│  domain/     vereditos, modelos, exceções       │  Fase 1 — zero deps do projeto
├─────────────────────────────────────────────────┤
│  llm/        LLMClient (Protocol) + adaptadores │  Fase 3
│              Gemini | Fake | Resilient          │
└─────────────────────────────────────────────────┘
```

## Regras de dependência

1. `domain` não importa nenhum outro módulo do projeto.
2. `parsing` e `state` dependem apenas de `domain` (e biblioteca padrão/Pydantic).
3. `llm` depende apenas de `domain`; **traduz erros tipados dos SDKs** para exceções de
   domínio — nunca string matching em mensagens de erro.
4. `services` orquestra `agents`, `parsing`, `state` e `llm`; não importa `tui` nem SDKs.
5. `tui` consome `services` por injeção de dependência; nenhuma regra de negócio na UI.

## Módulos implementados

### `domain/` (Fase 1)

- `verdicts.py` — enums de veredito. Os **valores** são os tokens PT-BR do contrato de
  prompt v1 (`"POSITIVO"`, `"ORGÂNICO"`...); os **nomes** seguem o inglês do código.
- `models.py` — resultados das análises (`MagiAnalysis`, `SeeleReport`, `VetoResult`...),
  Pydantic imutáveis (`frozen=True`). Veredito `None` = INDETERMINADO (saída fora do
  contrato, texto bruto preservado).
- `exceptions.py` — exceções temáticas (`ATFieldInterference` = rate limit,
  `CentralDogmaLockdown` = falha de infra, `AngelPatternDetected`).

### `parsing/` (Fase 1)

Parser **puro e tolerante** das saídas textuais dos agentes: uma função por tipo de
veredito. Tolerante a caixa alta/baixa, ausência de acentos, negrito markdown
(`**VOTO: ...**`) e espaçamento irregular; o último marcador vence. Nunca lança exceção.

### `state/` (Fase 2)

- `models.py` — `DogmaState` (schema v2, imutável): substitui os dois JSONs redundantes
  da v1 (`dogma_registry.json` + `paradigm_lock.json`).
- `store.py` — `StateStore` (Protocol), `JsonStateStore` (escrita atômica: tmp único por
  chamada + `os.replace`; arquivo corrompido vira `.bak` e é recriado) e
  `InMemoryStateStore`.
- `clock.py` — `Clock` (Protocol), `SystemClock`, `FixedClock`: toda regra temporal
  recebe o relógio por injeção.
- `cooldown.py` — `ParadigmCooldownService`: maturação de 100 dias, cooldown pós-uso,
  penalidade (reinicia cronômetro) e chave horária MD5.
- `migration.py` — `migrate_legacy`/`migrate_into`: mescla tolerante dos dois arquivos
  v1 (first_boot mais antigo; lock tem precedência no último uso; contadores do registry).

### `llm/` (Fase 3)

- `base.py` — Protocol assíncrono `LLMClient.complete(prompt) -> str`.
- `fake.py` — `FakeLLMClient` scriptado para a suíte de testes.
- `resilient.py` — `ResilientLLMClient` (timeout + retry com backoff exponencial e sleep injetável).
- `gemini.py` — adaptador Gemini via SDK oficial `google-genai` (import lazy, extra opcional).

### `agents/` (Fase 4)

- `spec.py` — `AgentSpec` imutável (`id`, `name`, `color`, `verdict`, `prompt_file`).
- `registry.py` — catálogo estático dos 7 agentes temáticos (`MELCHIOR`, `BALTHASAR`, `CASPER`, `SEELE`, `ADAM`, `LILITH`, `LONGINUS`).
- `base.py` — `Agent` (combina spec + `LLMClient`, renderiza prompt seguro com `{query}` e faz parsing tipado).
- `prompts/` — templates markdown versionados para cada agente.

### `services/` (Fase 5)

- `veto.py` — `LonginusVetoService`: verificação de regras invioláveis e registro de ativações.
- `magi.py` — `MagiCouncil`: deliberação em paralelo (`asyncio.gather`) com circuit breaker de veto.
- `seele.py` — `SeeleMonitor`: monitoramento silencioso em background e análise explícita com contagem de intervenções.
- `paradigm.py` — `ParadigmService`: orquestração Progenitora (ADAM vs. LILITH em paralelo), travas de maturação/cooldown, validação de chave horária e penalidade de veto.
- `dialect.py` — `DialectService`: debate dialético multi-rodadas com alternância de contexto cruzado entre unidades MAGI.
- `status.py` — `StatusService`: métricas operacionais consolidadas e contadores de sessão.
- `dossier.py` — `DossierService`: consulta a perfis e diretrizes centrais dos agentes.

## Módulos planejados

- **`tui/` (Fase 6)** — app Textual: painéis MAGI ao vivo, StatusBar com cooldown,
  command palette, telas de help/dossiê.

## Decisões registradas

Ver [`adr/`](adr/):

- [ADR 0001](adr/0001-uv-e-src-layout.md) — uv + src layout
- [ADR 0002](adr/0002-camada-llm-provider-agnostica.md) — camada LLM provider-agnóstica
- [ADR 0003](adr/0003-tui-textual.md) — TUI com Textual
- [ADR 0004](adr/0004-state-store-unificado.md) — state store unificado
