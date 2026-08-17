# ADR 0004 — State store unificado

- **Status**: Aceito (implementado na Fase 2)
- **Data**: 2026-08-16

## Contexto

A v1 mantém **dois arquivos de estado paralelos e redundantes**:
`dogma_registry.json` (persistence.py) e `paradigm_lock.json` (system.py), com lógicas
de cooldown do Paradigm duplicadas e divergentes, e dois mecanismos de chave/senha
(o MD5 horário do registry nunca é usado; a "senha" HH-MM-DD do system.py é apenas o
relógio). Escritas não são atômicas e JSON corrompido derruba o sistema.

## Decisão

- Um único modelo **`DogmaState`** (Pydantic imutável, `schema_version=2`).
- **`StateStore` (Protocol)** com `JsonStateStore` (escrita atômica: tmp único por
  chamada via `tempfile.mkstemp` no mesmo diretório + `os.replace`; arquivo corrompido
  vira `.bak` e é recriado) e `InMemoryStateStore` (testes).
- **`ParadigmCooldownService`** concentra todas as regras temporais (maturação de 100
  dias, cooldown, penalidade) e a chave horária MD5, com **`Clock` injetável**.
- **`migrate_legacy`** mescla os arquivos v1 de forma tolerante: first_boot mais
  antigo; lock tem precedência para último uso; contadores vêm do registry.
- A "senha" HH-MM-DD é descontinuada; permanece apenas a chave MD5 horária.

## Consequências

- Uma única fonte de verdade para cooldown e contadores; fim da divergência v1.
- Falhas de I/O degradam com segurança (backup + estado novo), nunca quebram o boot.
- Regras temporais testáveis sem esperar 100 dias (FixedClock + time-machine).
- Escritores concorrentes não corrompem o arquivo (garantia coberta por teste).
