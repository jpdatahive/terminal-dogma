# ADR 0003 — TUI com Textual

- **Status**: Aceito (implementação na Fase 6)
- **Data**: 2026-08-16

## Contexto

A v1 é um REPL com Rich: um loop `input()` bloqueante em que os três agentes MAGI são
consultados **sequencialmente**, a UI (`ui.py`, 736 linhas) mistura renderização,
conteúdo de dossiês e sanitização, e a SEELE "em background" é na verdade uma chamada
síncrona com `time.sleep`.

## Decisão

A interface da v2 será uma **TUI com Textual** (mesma equipe do Rich):

- Painéis por agente atualizando **ao vivo** conforme cada análise assíncrona retorna.
- SEELE como task async de verdade; StatusBar com cooldown do Paradigm e contadores.
- Command palette para `magi`, `seele`, `paradigm`, `veto`, `dialect`, `dossier`.
- A TUI consome `services` por injeção de dependência — nenhuma regra de negócio na UI.
- Testes com `textual.pilot.Pilot` (interação programática) + snapshot tests.

## Consequências

- Concorrência real (MAGI em paralelo) visível na interface.
- UI testável automaticamente, algo impossível no REPL bloqueante da v1.
- Curva de aprendizado do Textual mitigada pela ordem das fases: os serviços já
  estarão prontos e testados quando a UI for construída.
