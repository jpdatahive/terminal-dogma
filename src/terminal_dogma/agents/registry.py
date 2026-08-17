"""Catálogo dos agentes do Terminal Dogma (identidades herdadas da v1)."""

from terminal_dogma.agents.spec import AgentSpec
from terminal_dogma.domain.verdicts import VerdictKind

MELCHIOR = AgentSpec(
    id="melchior-01",
    name="MELCHIOR-01",
    color="bold blue",
    verdict=VerdictKind.MAGI_VOTE,
    prompt_file="melchior-01.md",
)
BALTHASAR = AgentSpec(
    id="balthasar-02",
    name="BALTHASAR-02",
    color="bold green",
    verdict=VerdictKind.MAGI_VOTE,
    prompt_file="balthasar-02.md",
)
CASPER = AgentSpec(
    id="casper-03",
    name="CASPER-03",
    color="bold yellow",
    verdict=VerdictKind.MAGI_VOTE,
    prompt_file="casper-03.md",
)
SEELE = AgentSpec(
    id="seele",
    name="SEELE_INTERJECTOR",
    color="bold magenta",
    verdict=VerdictKind.SEELE_REPORT,
    prompt_file="seele.md",
)
ADAM = AgentSpec(
    id="adam",
    name="ADAM_CATALYST",
    color="bold cyan",
    verdict=VerdictKind.POTENTIAL,
    prompt_file="adam.md",
)
LILITH = AgentSpec(
    id="lilith",
    name="LILITH_FOUNDATION",
    color="bold white",
    verdict=VerdictKind.ALIGNMENT,
    prompt_file="lilith.md",
)
LONGINUS = AgentSpec(
    id="longinus",
    name="LONGINUS_VETO",
    color="bold red",
    verdict=VerdictKind.VETO,
    prompt_file="longinus.md",
)

#: As três unidades votantes do conselho MAGI.
MAGI_UNITS: tuple[AgentSpec, ...] = (MELCHIOR, BALTHASAR, CASPER)

#: Todos os agentes registrados, em ordem de apresentação.
ALL_AGENTS: tuple[AgentSpec, ...] = (MELCHIOR, BALTHASAR, CASPER, SEELE, ADAM, LILITH, LONGINUS)

#: Lookup por id (usado por comandos como ``dossier`` e ``dialect``).
AGENTS_BY_ID: dict[str, AgentSpec] = {spec.id: spec for spec in ALL_AGENTS}
