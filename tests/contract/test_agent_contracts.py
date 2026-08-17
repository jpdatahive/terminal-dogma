"""Testes de contrato dos agentes: specs, templates de prompt e parsing.

Garantem que cada agente registrado:
- tem identidade única e template de prompt versionado e seguro para
  substituição (contém ``{query}`` e nenhuma outra chave);
- tem seu nome dentro do prompt (permite roteamento por substring no
  ``FakeLLMClient``);
- produz saída parseável: dentro do contrato → veredito tipado correto;
  fora do contrato → degrada para indeterminado sem exceção.
"""

import pytest

from terminal_dogma.agents import AGENTS_BY_ID, ALL_AGENTS, MAGI_UNITS, Agent
from terminal_dogma.agents.spec import QUERY_PLACEHOLDER
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
    VerdictKind,
    VetoStatus,
)
from terminal_dogma.llm import FakeLLMClient
from terminal_dogma.parsing import parse_output

VALID_OUTPUTS = {
    VerdictKind.MAGI_VOTE: "Análise lógica detalhada.\nVOTO: POSITIVO",
    VerdictKind.SEELE_REPORT: (
        "INTERVENÇÃO: NÃO\nANÁLISE: Risco moderado.\nALERTA: Nenhum risco crítico."
    ),
    VerdictKind.POTENTIAL: "Análise visionária.\nPOTENCIAL: DISRUPTIVO",
    VerdictKind.ALIGNMENT: "Análise cultural.\nALINHAMENTO: ORGÂNICO",
    VerdictKind.VETO: "NENHUM VETO",
}

EXPECTED_TYPES = {
    VerdictKind.MAGI_VOTE: MagiAnalysis,
    VerdictKind.SEELE_REPORT: SeeleReport,
    VerdictKind.POTENTIAL: PotentialAssessment,
    VerdictKind.ALIGNMENT: AlignmentAssessment,
    VerdictKind.VETO: VetoResult,
}

EXPECTED_VERDICTS = {
    VerdictKind.MAGI_VOTE: ("vote", MagiVote.POSITIVE),
    VerdictKind.SEELE_REPORT: ("intervention", False),
    VerdictKind.POTENTIAL: ("potential", ParadigmPotential.DISRUPTIVE),
    VerdictKind.ALIGNMENT: ("alignment", LilithAlignment.ORGANIC),
    VerdictKind.VETO: ("status", VetoStatus.NO_VETO),
}


class TestRegistry:
    def test_sete_agentes_registrados(self):
        assert len(ALL_AGENTS) == 7
        assert len(AGENTS_BY_ID) == 7

    def test_ids_e_nomes_sao_unicos(self):
        assert len({s.id for s in ALL_AGENTS}) == len(ALL_AGENTS)
        assert len({s.name for s in ALL_AGENTS}) == len(ALL_AGENTS)

    def test_unidades_magi_sao_os_tres_votantes_da_v1(self):
        assert {s.name for s in MAGI_UNITS} == {"MELCHIOR-01", "BALTHASAR-02", "CASPER-03"}
        assert all(s.verdict is VerdictKind.MAGI_VOTE for s in MAGI_UNITS)

    def test_agentes_tem_cores_tematicas_da_v1(self):
        expected_colors = {
            "melchior-01": "bold blue",
            "balthasar-02": "bold green",
            "casper-03": "bold yellow",
            "seele": "bold magenta",
            "adam": "bold cyan",
            "lilith": "bold white",
            "longinus": "bold red",
        }
        assert {s.id: s.color for s in ALL_AGENTS} == expected_colors


class TestPromptTemplates:
    @pytest.mark.parametrize("spec", ALL_AGENTS, ids=lambda s: s.id)
    def test_prompt_existe_e_e_seguro_para_substituicao(self, spec):
        template = spec.load_prompt()
        assert QUERY_PLACEHOLDER in template
        # Sem o placeholder, nenhuma outra chave pode restar no template.
        rest = template.replace(QUERY_PLACEHOLDER, "")
        assert "{" not in rest
        assert "}" not in rest

    @pytest.mark.parametrize("spec", ALL_AGENTS, ids=lambda s: s.id)
    def test_prompt_define_persona_e_formato_de_saida(self, spec):
        template = spec.load_prompt()
        assert "FORMATO DE SAÍDA" in template
        assert len(template) > 500  # prompts são fichas de persona completas


class TestOutputContracts:
    @pytest.mark.parametrize("spec", ALL_AGENTS, ids=lambda s: s.id)
    def test_saida_valida_produz_modelo_e_veredito_corretos(self, spec):
        result = parse_output(spec.verdict, VALID_OUTPUTS[spec.verdict])
        assert isinstance(result, EXPECTED_TYPES[spec.verdict])
        field, expected = EXPECTED_VERDICTS[spec.verdict]
        assert getattr(result, field) == expected

    @pytest.mark.parametrize("spec", ALL_AGENTS, ids=lambda s: s.id)
    def test_saida_malformada_degrada_para_indeterminado_sem_excecao(self, spec):
        result = parse_output(spec.verdict, "saída completamente fora do contrato")
        match result:
            case MagiAnalysis(vote=None):
                pass
            case SeeleReport(intervention=False):
                pass
            case PotentialAssessment(potential=None):
                pass
            case AlignmentAssessment(alignment=None):
                pass
            case VetoResult(status=VetoStatus.INDETERMINATE):
                pass
            case _:
                pytest.fail(f"{spec.id}: saída malformada não degradou para indeterminado")


class TestAgent:
    async def test_analyze_renderiza_prompt_consulta_llm_e_faz_parse(self):
        fake = FakeLLMClient(default="Análise empírica.\nVOTO: POSITIVO")
        agent = Agent(AGENTS_BY_ID["melchior-01"], fake)

        result = await agent.analyze("Devemos adotar energia solar?")

        assert isinstance(result, MagiAnalysis)
        assert result.vote == MagiVote.POSITIVE
        (sent,) = fake.calls
        assert "Devemos adotar energia solar?" in sent
        assert QUERY_PLACEHOLDER not in sent

    async def test_analyze_com_saida_malformada_nao_quebra(self):
        agent = Agent(AGENTS_BY_ID["longinus"], FakeLLMClient(default="texto confuso"))
        result = await agent.analyze("qualquer coisa")
        assert result == VetoResult(status=VetoStatus.INDETERMINATE, raw="texto confuso")

    async def test_nome_do_agente_vem_da_spec(self):
        agent = Agent(AGENTS_BY_ID["seele"], FakeLLMClient())
        assert agent.name == "SEELE_INTERJECTOR"
