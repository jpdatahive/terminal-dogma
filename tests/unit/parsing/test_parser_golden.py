"""Testes do parser contra golden files.

Os arquivos em ``golden/`` reproduzem os formatos do contrato de prompt v1
(ver ``src/dogma_core/agents.py``): saídas válidas, com markdown, em
minúsculas e malformadas. ``expected.json`` declara o resultado esperado
de cada arquivo.
"""

import json
from pathlib import Path

import pytest

from terminal_dogma.domain.verdicts import (
    LilithAlignment,
    MagiVote,
    ParadigmPotential,
    VetoStatus,
)
from terminal_dogma.parsing import (
    parse_alignment,
    parse_magi_vote,
    parse_potential,
    parse_seele_report,
    parse_veto,
)

GOLDEN_DIR = Path(__file__).parent / "golden"


def _load_cases() -> list[tuple[str, dict]]:
    expected = json.loads((GOLDEN_DIR / "expected.json").read_text(encoding="utf-8"))
    return list(expected.items())


@pytest.mark.parametrize(("filename", "spec"), _load_cases())
def test_golden(filename: str, spec: dict):
    text = (GOLDEN_DIR / filename).read_text(encoding="utf-8")
    kind = spec["parser"]

    if kind == "magi":
        result = parse_magi_vote(text)
        expected_vote = MagiVote(spec["vote"]) if spec["vote"] else None
        assert result.vote == expected_vote
        assert spec["analysis_contains"] in result.analysis
    elif kind == "seele":
        result = parse_seele_report(text)
        assert result.intervention is spec["intervention"]
        assert spec["analysis_contains"] in result.analysis
        if spec["alert_contains"] is None:
            assert result.alert is None
        else:
            assert result.alert is not None
            assert spec["alert_contains"] in result.alert
    elif kind == "potential":
        result = parse_potential(text)
        assert result.potential == ParadigmPotential(spec["potential"])
        assert spec["analysis_contains"] in result.analysis
    elif kind == "alignment":
        result = parse_alignment(text)
        assert result.alignment == LilithAlignment(spec["alignment"])
        assert spec["analysis_contains"] in result.analysis
    elif kind == "veto":
        result = parse_veto(text)
        assert result.status == VetoStatus(spec["status"])
        if spec.get("violated_rule") is None and "violated_rule_contains" not in spec:
            assert result.violated_rule is None
        if "violated_rule_contains" in spec:
            assert result.violated_rule is not None
            assert spec["violated_rule_contains"] in result.violated_rule
        assert result.raw == text
    else:  # pragma: no cover - erro de digitação no expected.json
        raise AssertionError(f"Parser desconhecido no golden: {kind}")
