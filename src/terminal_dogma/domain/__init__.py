"""Núcleo de domínio do Terminal Dogma (zero dependências do projeto)."""

from terminal_dogma.domain.exceptions import (
    AngelPatternDetected,
    ATFieldInterference,
    CentralDogmaLockdown,
    DogmaSystemException,
)
from terminal_dogma.domain.models import (
    AgentDossier,
    AlignmentAssessment,
    AnalysisResult,
    DialectDebate,
    DialectRound,
    MagiAnalysis,
    MagiDeliberation,
    ParadigmExecution,
    PotentialAssessment,
    SeeleReport,
    SystemStatus,
    VetoResult,
)
from terminal_dogma.domain.verdicts import (
    LilithAlignment,
    MagiVote,
    ParadigmPotential,
    VerdictKind,
    VetoStatus,
)

__all__ = [
    "ATFieldInterference",
    "AgentDossier",
    "AlignmentAssessment",
    "AnalysisResult",
    "AngelPatternDetected",
    "CentralDogmaLockdown",
    "DialectDebate",
    "DialectRound",
    "DogmaSystemException",
    "LilithAlignment",
    "MagiAnalysis",
    "MagiDeliberation",
    "MagiVote",
    "ParadigmExecution",
    "ParadigmPotential",
    "PotentialAssessment",
    "SeeleReport",
    "SystemStatus",
    "VerdictKind",
    "VetoResult",
    "VetoStatus",
]
