import unittest
from unittest.mock import MagicMock
import sys
import os

# Adiciona o diretório src ao path para que possamos importar dogma_core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from dogma_core.system import DogmaSystem

class TestDogmaSystem(unittest.TestCase):

    def setUp(self):
        # Mock da UI para evitar saídas no console durante os testes
        self.mock_ui = MagicMock()
        
        # Mock dos agentes para evitar chamadas de API
        self.mock_agents = {
            'melchior': MagicMock(),
            'balthasar': MagicMock(),
            'casper': MagicMock(),
            'adam': MagicMock(),
            'lilith': MagicMock(),
            'seele': MagicMock(),
            'longinus': MagicMock(),
        }

        # Instancia DogmaSystem com os mocks
        # Precisamos mockar os agentes antes de instanciar o sistema
        with (
            unittest.mock.patch('dogma_core.system.ui.UIController', return_value=self.mock_ui),
            unittest.mock.patch('dogma_core.system.agents.MelchiorAgent', return_value=self.mock_agents['melchior']),
            unittest.mock.patch('dogma_core.system.agents.BalthasarAgent', return_value=self.mock_agents['balthasar']),
            unittest.mock.patch('dogma_core.system.agents.CasperAgent', return_value=self.mock_agents['casper']),
            unittest.mock.patch('dogma_core.system.agents.AdamAgent', return_value=self.mock_agents['adam']),
            unittest.mock.patch('dogma_core.system.agents.LilithAgent', return_value=self.mock_agents['lilith']),
            unittest.mock.patch('dogma_core.system.agents.SeeleAgent', return_value=self.mock_agents['seele']),
            unittest.mock.patch('dogma_core.system.agents.LonginusAgent', return_value=self.mock_agents['longinus'])
        ):
            self.system = DogmaSystem()

    def test_parse_analysis_magi_vote(self):
        """Testa o parsing de um voto padrão do MAGI."""
        full_text = "Esta é a análise.\nVOTO: POSITIVO"
        result = self.system._parse_analysis(full_text)
        self.assertEqual(result['analysis'], "Esta é a análise.")
        self.assertEqual(result['verdict'], "VOTO: POSITIVO")

    def test_parse_analysis_seele_intervention(self):
        """Testa o parsing de uma intervenção do SEELE."""
        full_text = "INTERVENÇÃO: SIM\nANÁLISE: Análise de risco detalhada.\nALERTA: Risco existencial detectado."
        result = self.system._parse_analysis(full_text)
        self.assertEqual(result['intervention'], "SIM")
        self.assertEqual(result['analysis'], "Análise de risco detalhada.")
        self.assertEqual(result['verdict'], "Risco existencial detectado.")

    def test_parse_analysis_adam_potential(self):
        """Testa o parsing de um veredito de potencial do ADAM."""
        full_text = "Análise do potencial disruptivo.\nPOTENCIAL: DISRUPTIVO"
        result = self.system._parse_analysis(full_text)
        self.assertEqual(result['analysis'], "Análise do potencial disruptivo.")
        self.assertEqual(result['verdict'], "POTENCIAL: DISRUPTIVO")

    def test_parse_analysis_lilith_alignment(self):
        """Testa o parsing de um veredito de alinhamento da LILITH."""
        full_text = "Análise do alinhamento cultural.\nALINHAMENTO: ORGÂNICO"
        result = self.system._parse_analysis(full_text)
        self.assertEqual(result['analysis'], "Análise do alinhamento cultural.")
        self.assertEqual(result['verdict'], "ALINHAMENTO: ORGÂNICO")

    def test_parse_analysis_longinus_veto(self):
        """Testa o parsing de um veto da LONGINUS."""
        full_text = "VETO ACIONADO: Violação direta de princípios éticos fundamentais."
        result = self.system._parse_analysis(full_text)
        # No caso de veto, a análise é o próprio texto
        self.assertEqual(result['analysis'], "")
        self.assertEqual(result['verdict'], "VETO ACIONADO: Violação direta de princípios éticos fundamentais.")

    def test_parse_analysis_no_verdict(self):
        """Testa o parsing quando não há um veredito claro."""
        full_text = "Apenas um texto de análise sem um veredito formatado."
        result = self.system._parse_analysis(full_text)
        self.assertEqual(result['analysis'], full_text)
        self.assertEqual(result['verdict'], "INDETERMINADO")

if __name__ == '__main__':
    unittest.main()
