# Testes — Terminal Dogma v2

## Filosofia: TDD

Todo código novo segue o ciclo **red → green → refactor**:

1. Escreve-se o teste que falha (commit `test: ...`, vermelho confirmado).
2. Implementa-se o mínimo para passar (commit `feat: ...`, verde confirmado).
3. Refatora-se com a suíte verde.

Todo bug corrigido vira um teste de regressão **antes** da correção. Exemplos reais do
projeto: colisão de arquivo tmp entre escritores concorrentes no `JsonStateStore` e
`strip("*")` agressivo no parser de veto — ambos detectados pelos testes, não por inspeção.

## Estrutura

```
tests/
├── unit/         # lógica pura: parser, state, domain (a maioria dos testes)
├── contract/     # contrato de saída de cada agente com FakeLLM (Fase 4)
├── integration/  # fluxos completos de services com fakes (Fase 5)
├── tui/          # testes com Textual Pilot (Fase 6)
├── live/         # contra APIs reais — skip por padrão, exige chave
└── legacy/       # suíte v1 congelada (ignorada por padrão)
```

## Rodando

```bash
uv run pytest                                   # suíte v2
uv run pytest --cov=src/terminal_dogma --cov-report=term-missing --cov-fail-under=85
uv run pytest tests/live -m live                # só com GOOGLE_API_KEY definida
```

## Técnicas por camada

| Camada | Técnica |
|--------|---------|
| `parsing` | **Golden files** (`tests/unit/parsing/golden/`) reproduzindo o contrato v1 + **hypothesis** (nunca lança exceção; saída dentro do contrato faz round-trip exato) |
| `state` | `tmp_path` para I/O real, `FixedClock` injetado para regras temporais, **time-machine** no teste de integração com `SystemClock`, `ThreadPoolExecutor` para escritores concorrentes |
| `llm` | `FakeLLMClient` scriptado; erros tipados reais do SDK simulados via mock; sleep injetável (sem espera real em testes de retry) |
| `tui` | `Textual Pilot` + snapshot tests (Fase 6) |

## Configuração relevante

- `tests/conftest.py` registra o perfil hypothesis `default` com `deadline=None`
  (o primeiro exemplo gerado tem overhead variável entre máquinas).
- Cobertura mínima de 85% é exigida no CI; o core está em 100%.
- O marcador `live` está registrado em `pyproject.toml`; testes live usam
  `skipif` quando a chave de API não está definida.
