"""Casos de borda do parser (além dos golden files)."""

from terminal_dogma.domain.verdicts import MagiVote, VetoStatus
from terminal_dogma.parsing import parse_magi_vote, parse_seele_report, parse_veto


class TestParseMagiVote:
    def test_ultimo_marcador_vence_quando_ha_repeticao(self):
        text = "Primeira impressão.\nVOTO: POSITIVO\nReconsiderando os dados.\nVOTO: NEGATIVO"
        result = parse_magi_vote(text)
        assert result.vote == MagiVote.NEGATIVE
        assert "Primeira impressão." in result.analysis
        assert "Reconsiderando os dados." in result.analysis

    def test_string_vazia_degrada_para_indeterminado(self):
        result = parse_magi_vote("")
        assert result.analysis == ""
        assert result.vote is None

    def test_marcador_sem_espaco_apos_dois_pontos(self):
        result = parse_magi_vote("Análise direta.\nVOTO:POSITIVO")
        assert result.vote == MagiVote.POSITIVE


class TestParseSeeleReport:
    def test_intervencao_sem_alerta(self):
        text = "INTERVENÇÃO: SIM\nANÁLISE: Risco crítico sem frase de alerta."
        result = parse_seele_report(text)
        assert result.intervention is True
        assert "Risco crítico" in result.analysis
        assert result.alert is None

    def test_marcadores_sem_acento(self):
        text = "INTERVENCAO: NAO\nANALISE: Sem riscos relevantes.\nALERTA: Nada a relatar."
        result = parse_seele_report(text)
        assert result.intervention is False
        assert "Sem riscos" in result.analysis
        assert result.alert == "Nada a relatar."

    def test_sem_marcador_de_intervencao_preserva_texto_completo(self):
        text = "Prosa pessimista sem estrutura de contrato."
        result = parse_seele_report(text)
        assert result.intervention is False
        assert result.analysis == text
        assert result.alert is None

    def test_intervencao_sem_marcador_de_analise_usa_texto_anterior(self):
        text = "Contexto preliminar do comitê.\nINTERVENÇÃO: SIM"
        result = parse_seele_report(text)
        assert result.intervention is True
        assert result.analysis == "Contexto preliminar do comitê."
        assert result.alert is None


class TestParseVeto:
    def test_veto_acionado_tem_prioridade_sobre_nenhum_veto_no_texto(self):
        text = "NENHUM VETO seria esperado, porém: VETO ACIONADO: regra fundamental violada"
        result = parse_veto(text)
        assert result.status == VetoStatus.VETO_TRIGGERED
        assert result.vetoed is True
        assert result.violated_rule == "regra fundamental violada"

    def test_regra_multilinha_e_colapsada_em_uma_linha(self):
        text = "VETO ACIONADO: Primeira parte da regra\ncontinua em outra linha."
        result = parse_veto(text)
        assert result.violated_rule == "Primeira parte da regra continua em outra linha."

    def test_veto_acionado_sem_regra_tem_violated_rule_none(self):
        result = parse_veto("VETO ACIONADO:")
        assert result.status == VetoStatus.VETO_TRIGGERED
        assert result.violated_rule is None

    def test_regra_em_negrito_e_desembrulhada(self):
        result = parse_veto("VETO ACIONADO: **Ameaça à soberania da organização.**")
        assert result.violated_rule == "Ameaça à soberania da organização."
