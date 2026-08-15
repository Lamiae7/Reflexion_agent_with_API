"""
Assemblage du graphe LangGraph : Responder -> execute_tools -> Revisor,
avec une boucle conditionnelle (event_loop) qui relance une recherche +
révision tant que le nombre maximum d'itérations n'est pas atteint.

Reprend fidèlement la logique du notebook d'origine, encapsulée dans une
fonction `build_graph()` réutilisable (par l'API, par des tests, etc.).
"""
import json
import logging
from typing import List

from langchain_core.messages import BaseMessage, ToolMessage
from langgraph.graph import END, MessageGraph

from app.agent.chains import build_responder_chain, build_revisor_chain
from app.agent.tools import get_search_tool
from app.config import get_settings


from langchain_core.runnables import RunnableLambda

logger = logging.getLogger(__name__)


def make_execute_tools():
    """Crée le node `execute_tools` : exécute les requêtes de recherche
    générées par le Responder/Revisor et renvoie les résultats sous forme
    de ToolMessage."""
    search_tool = get_search_tool()

    def execute_tools(state: List[BaseMessage]) -> List[BaseMessage]:
        last_ai_message = state[-1]
        tool_messages = []
        for tool_call in last_ai_message.tool_calls: # cette fonction exécute les requettes contenus dans le dernier message
            if tool_call["name"] in ("AnswerQuestion", "ReviseAnswer"):
                call_id = tool_call["id"]
                search_queries = tool_call["args"].get("search_queries", [])
                query_results = {}
                for query in search_queries:
                    logger.info("Recherche web: %s", query)
                    query_results[query] = search_tool.invoke(query)
                tool_messages.append(
                    ToolMessage(
                        content=json.dumps(query_results), tool_call_id=call_id
                    )
                )
        return tool_messages

    return execute_tools


def make_event_loop(max_iterations: int):
    """Crée la fonction de routage conditionnel : continue tant que le
    nombre de passages par `execute_tools` (= nombre de recherches déjà
    effectuées) est inférieur à `max_iterations`."""

    def event_loop(state: List[BaseMessage]) -> str:
        num_iterations = sum(isinstance(item, ToolMessage) for item in state)
        if num_iterations >= max_iterations:
            return END
        return "execute_tools"

    return event_loop


def build_graph():
    """Construit et compile le graphe Reflexion complet."""
    settings = get_settings()

    responder_chain = build_responder_chain()
    revisor_chain = build_revisor_chain()
    execute_tools = make_execute_tools()
    event_loop = make_event_loop(settings.max_iterations) # voir la classe settings dans config.py pour voir max_iterations.

    graph = MessageGraph()
    graph.add_node("respond", responder_chain)
    graph.add_node("execute_tools", execute_tools)
    graph.add_node("revisor", revisor_chain)

    graph.add_edge("respond", "execute_tools")
    graph.add_edge("execute_tools", "revisor")
    graph.add_conditional_edges("revisor", event_loop) # on appelle le revisor a chaque fois que event loop n'est pas en END.
    graph.set_entry_point("respond")

    return graph.compile()
