"""Núcleo de domínio do Terminal Dogma (zero dependências do projeto)."""

from terminal_dogma.domain.exceptions import (
    AngelPatternDetected,
    ATFieldInterference,
    CentralDogmaLockdown,
    DogmaSystemException,
)
from terminal_dogma.domain.models import (
    AlignmentAssessment,
    MagiAnalysis,
    PotentialAssessment,
    SeeleReport,
    VetoResult,
)
from terminal_dogma.domain.verdicts import (
    LilithAlignment,
    MagiVote,
    ParadigmPotential,
    VetoStatus,
)

__all__ = [
    "ATFieldInterference",
    "AlignmentAssessment",
    "AngelPatternDetected",
    "CentralDogmaLockdown",
    "DogmaSystemException",
    "LilithAlignment",
    "MagiAnalysis",
    "MagiVote",
    "ParadigmPotential",
    "PotentialAssessment",
    "SeeleReport",
    "VetoResult",
    "VetoStatus",
]
