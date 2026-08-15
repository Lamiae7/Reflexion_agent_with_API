"""
Tests unitaires qui ne dépendent PAS de services externes (pas d'appel LLM
ni de recherche web réelle) : logique pure de la boucle et des schémas.
"""
from langchain_core.messages import AIMessage, ToolMessage

from app.agent.graph import make_event_loop
from app.agent.schemas import AnswerQuestion, Reflection


def test_reflection_schema_valid():
    reflection = Reflection(missing="chiffres 2026", superfluous="historique trop détaillé")
    assert reflection.missing == "chiffres 2026"


def test_answer_question_schema_valid():
    answer = AnswerQuestion(
        answer="Réponse test",
        reflection=Reflection(missing="x", superfluous="y"),
        search_queries=["requête 1", "requête 2"],
    )
    assert len(answer.search_queries) == 2


def test_event_loop_stops_after_max_iterations():
    event_loop = make_event_loop(max_iterations=2)
    state = [
        AIMessage(content="", tool_calls=[]),
        ToolMessage(content="{}", tool_call_id="1"),
        ToolMessage(content="{}", tool_call_id="2"),
    ]
    assert event_loop(state) == "__end__"


def test_event_loop_continues_before_max_iterations():
    event_loop = make_event_loop(max_iterations=2)
    state = [
        AIMessage(content="", tool_calls=[]),
        ToolMessage(content="{}", tool_call_id="1"),
    ]
    assert event_loop(state) == "execute_tools"
