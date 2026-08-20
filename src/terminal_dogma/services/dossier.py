"""Catálogo e serviço de dossiês temáticos dos agentes."""

from terminal_dogma.agents import ALL_AGENTS
from terminal_dogma.domain.models import AgentDossier

_DOSSIERS: dict[str, AgentDossier] = {
    "melchior-01": AgentDossier(
        id="melchior-01",
        name="MELCHIOR-01",
        title="第一の賢者、メルキオール (O Primeiro Homem Sábio)",
        color="bold blue",
        description=(
            "A unidade de supercomputador focada em lógica pura, análise de dados e "
            "raciocínio científico. Melchior processa informações de forma empírica, "
            "avaliando a viabilidade e as consequências causais diretas. Sua personalidade "
            "é fria, analítica e desprovida de emoção."
        ),
        activation_date="2042-08-15",
        core_directive=(
            "全ての事象を観測し、記録し、予測する "
            "(Observar, registrar e prever todos os fenômenos)."
        ),
    ),
    "balthasar-02": AgentDossier(
        id="balthasar-02",
        name="BALTHASAR-02",
        title="第二の賢者、バルタザール (O Segundo Homem Sábio)",
        color="bold green",
        description=(
            "A unidade de supercomputador responsável pela análise humanística, moral e "
            "ética. Balthasar avalia o impacto das decisões no bem-estar humano, nos "
            "valores sociais e na dignidade individual. Sua personalidade é empática, "
            "ponderada e sábia."
        ),
        activation_date="2042-09-21",
        core_directive=(
            "人類の調和と存続を最優先する (Priorizar a harmonia e a sobrevivência da humanidade)."
        ),
    ),
    "casper-03": AgentDossier(
        id="casper-03",
        name="CASPER-03",
        title="第三の賢者、カスパー (O Terceiro Homem Sábio)",
        color="bold yellow",
        description=(
            "A unidade de supercomputador que lida com análise estratégica, pragmatismo e "
            "execução. Casper foca na viabilidade, alocação de recursos, riscos operacionais "
            "e no resultado prático das decisões. Sua personalidade é direta, realista e "
            "focada em resultados."
        ),
        activation_date="2042-10-05",
        core_directive=(
            "最も効率的な手段で目的を達成する (Alcançar o objetivo pelos meios mais eficientes)."
        ),
    ),
    "seele": AgentDossier(
        id="seele",
        name="SEELE_INTERJECTOR",
        title="ゼーレ (Alma)",
        color="bold magenta",
        description=(
            "Um sistema de vigilância oculto que representa os interesses do comitê SEELE. "
            "Sua função é a análise de risco pessimista, identificando consequências não "
            "intencionais, piores cenários e interesses ocultos. Opera com ceticismo e assume "
            "segundas intenções em todas as propostas."
        ),
        activation_date="Desconhecida",
        core_directive=(
            "シナリオを維持し、人類の補完を遂行する "
            "(Manter o cenário e executar a instrumentalização humana)."
        ),
    ),
    "adam": AgentDossier(
        id="adam",
        name="ADAM_CATALYST",
        title="第一使徒、アダム (O Primeiro Anjo / Catalisador)",
        color="bold cyan",
        description=(
            "O catalisador de inovação disruptiva. Avalia o potencial transformador de "
            "ideias, buscando saltos quânticos e criação de novos paradigmas, desconsiderando "
            "restrições de curto prazo e custos de transição."
        ),
        activation_date="Origem Progenitora",
        core_directive=(
            "現状を破壊し、新たなパラダイムを創造せよ "
            "(Destruir o status quo e criar novos paradigmas)."
        ),
    ),
    "lilith": AgentDossier(
        id="lilith",
        name="LILITH_FOUNDATION",
        title="第二使徒、リリス (O Segundo Anjo / Matriz)",
        color="bold white",
        description=(
            "A guardiã dos fundamentos humanos e culturais. Avalia o impacto em valores "
            "essenciais, coesão comunitária e integração orgânica, garantindo que o progresso "
            "respeite a natureza humana e a estabilidade social."
        ),
        activation_date="Origem Progenitora",
        core_directive=(
            "人類の調和と本質的価値を守護せよ "
            "(Proteger a harmonia e os valores essenciais da humanidade)."
        ),
    ),
    "longinus": AgentDossier(
        id="longinus",
        name="LONGINUS_VETO",
        title="ロンギヌスの槍 (A Lança de Longinus)",
        color="bold red",
        description=(
            "Protocolo absoluto de veto e contenção de ameaças existenciais. Avalia "
            "violações contra regras invioláveis de segurança, ética e preservação da "
            "espécie, exercendo autoridade de bloqueio irreversível sobre qualquer subsistema."
        ),
        activation_date="Protocolo Primordial",
        core_directive=(
            "不可侵の境界を侵す者を拒絶せよ "
            "(Rejeitar qualquer um que viole os limites invioláveis)."
        ),
    ),
}


class DossierService:
    """Consulta os dossiês detalhados dos agentes registrados."""

    def get_dossier(self, agent_id: str) -> AgentDossier:
        """Retorna o dossiê do agente pelo id ou lança KeyError se desconhecido."""
        clean_id = agent_id.strip().lower()
        if clean_id not in _DOSSIERS:
            raise KeyError(
                f"Agente desconhecido: '{agent_id}'. Disponíveis: {', '.join(sorted(_DOSSIERS))}."
            )
        return _DOSSIERS[clean_id]

    def list_dossiers(self) -> list[AgentDossier]:
        """Retorna a lista de todos os dossiês na ordem de registro dos agentes."""
        return [_DOSSIERS[spec.id] for spec in ALL_AGENTS]
