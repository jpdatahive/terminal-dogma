"""Testes do despacho de parsing por tipo de veredito (VerdictKind)."""

import pytest

from terminal_dogma.domain.models import (
    AlignmentAssessment,
    MagiAnalysis,
    PotentialAssessment,
    SeeleReport,
    VetoResult,
)
from terminal_dogma.domain.verdicts import VerdictKind
from terminal_dogma.parsing import PARSERS, parse_output


class TestParseOutput:
    @pytest.mark.parametrize(
        ("kind", "text", "expected_type"),
        [
            (VerdictKind.MAGI_VOTE, "Análise.\nVOTO: POSITIVO", MagiAnalysis),
            (
                VerdictKind.SEELE_REPORT,
                "INTERVENÇÃO: NÃO\nANÁLISE: Risco.\nALERTA: Nenhum.",
                SeeleReport,
            ),
            (VerdictKind.POTENTIAL, "Análise.\nPOTENCIAL: INCREMENTAL", PotentialAssessment),
            (VerdictKind.ALIGNMENT, "Análise.\nALINHAMENTO: ORGÂNICO", AlignmentAssessment),
            (VerdictKind.VETO, "NENHUM VETO", VetoResult),
        ],
    )
    def test_despacha_para_o_parser_correto(self, kind, text, expected_type):
        assert isinstance(parse_output(kind, text), expected_type)

    def test_todos_os_kinds_tem_parser_registrado(self):
        assert set(PARSERS) == set(VerdictKind)
