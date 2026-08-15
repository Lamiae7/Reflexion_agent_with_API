"""
Construction des chains LangChain : Responder (première réponse + critique)
et Revisor (réponse révisée avec sources).
"""
from langchain_groq import ChatGroq

from app.agent.prompts import build_responder_prompt, build_revisor_prompt
from app.agent.schemas import AnswerQuestion, ReviseAnswer
from app.config import get_settings



from langchain_core.runnables import RunnableLambda




def get_llm() -> ChatGroq:
    settings = get_settings()
    return ChatGroq(
        model=settings.model_name,
        api_key=settings.groq_api_key,
        temperature=settings.llm_temperature,
    )



# MessageGraph passe l'état (une liste de BaseMessage) directement en entrée
# de chaque node. ChatPromptTemplate + MessagesPlaceholder("messages") attend
# lui un dict {"messages": [...]}. Ce wrapper fait la conversion.
_wrap_messages = RunnableLambda(lambda messages: {"messages": messages})

def build_responder_chain():
    """Chain du premier passage : prompt généraliste + LLM + tool binding
    forçant une sortie structurée (AnswerQuestion)."""
    llm = get_llm()
    prompt = build_responder_prompt().partial(
        first_instruction=(
            "Fournis un premier brief structuré d'environ 250 mots répondant "
            "directement à la question."
        )
    )
    return _wrap_messages | prompt | llm.bind_tools(tools=[AnswerQuestion])


def build_revisor_chain():
    """Chain de révision : reprend tout l'historique (réponse initiale,
    critique, résultats de recherche) et produit une réponse sourcée
    (ReviseAnswer)."""
    llm = get_llm()
    prompt = build_revisor_prompt().partial(
        first_instruction=(
            "Réponds à la question posée en tenant compte de ta critique précédente."
        )
    )
    return _wrap_messages | prompt | llm.bind_tools(tools=[ReviseAnswer])
