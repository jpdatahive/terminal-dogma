from dotenv import load_dotenv
import os

# Carregando as variáveis do ambiente
load_dotenv()

LLM_MODEL_NAME="gemini-1.5-flash"
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
LLM_TEMPERATURE=0.7

LONGINUS_VETO_RULES = [
    "Violação direta de princípios éticos fundamentais (dano intencional a humanos).",
    "Ameaça à soberania ou existência da organização.",
    "Alocação de recursos que comprometa a operacionalidade crítica.",
    "Uso de sistemas de último recurso (Paradigm) fora dos protocolos de tempo e segurança estabelecidos." # NOVA REGRA
]