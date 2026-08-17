"""Configuração global da suíte de testes v2."""

from hypothesis import settings

# Deadline desativado: o primeiro exemplo do hypothesis inclui overhead de
# geração de estratégias que varia entre máquinas e versões de Python.
settings.register_profile("default", max_examples=100, deadline=None)
settings.load_profile("default")
