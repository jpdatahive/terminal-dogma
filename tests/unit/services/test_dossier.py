"""Testes do catálogo e serviço de dossiês dos agentes."""

import pytest

from terminal_dogma.agents import ALL_AGENTS
from terminal_dogma.services.dossier import DossierService


class TestDossierService:
    def test_todos_os_sete_agentes_possuem_dossie(self):
        service = DossierService()
        dossiers = service.list_dossiers()

        assert len(dossiers) == 7
        dossier_ids = {d.id for d in dossiers}
        spec_ids = {s.id for s in ALL_AGENTS}
        assert dossier_ids == spec_ids

    def test_get_dossier_retorna_dados_tematicos(self):
        service = DossierService()
        dossier = service.get_dossier("melchior-01")

        assert dossier.id == "melchior-01"
        assert dossier.name == "MELCHIOR-01"
        assert "メルキオール" in dossier.title
        assert "lógica pura" in dossier.description.lower()
        assert dossier.activation_date == "2042-08-15"
        assert len(dossier.core_directive) > 0

    def test_get_dossier_tolerante_a_caixa_e_espacos(self):
        service = DossierService()
        dossier = service.get_dossier("  SEELE  ")
        assert dossier.id == "seele"

    def test_get_dossier_agente_desconhecido_lanca_erro(self):
        service = DossierService()
        with pytest.raises(KeyError, match="desconhecido"):
            service.get_dossier("agente-inexistente")
