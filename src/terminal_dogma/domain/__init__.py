"""Núcleo de domínio do Terminal Dogma (zero dependências do projeto)."""

from terminal_dogma.domain.exceptions import (
    AngelPatternDetected,
    ATFieldInterference,
    CentralDogmaLockdown,
    DogmaSystemException,
)
from terminal_dogma.domain.models import (
    AlignmentAssessment,
    AnalysisResult,
    MagiAnalysis,
    PotentialAssessment,
    SeeleReport,
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
    "AlignmentAssessment",
    "AnalysisResult",
    "AngelPatternDetected",
    "CentralDogmaLockdown",
    "DogmaSystemException",
    "LilithAlignment",
    "MagiAnalysis",
    "MagiVote",
    "ParadigmPotential",
    "PotentialAssessment",
    "SeeleReport",
    "VerdictKind",
    "VetoResult",
    "VetoStatus",
]
