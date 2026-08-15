"""
Test d'intégration de l'endpoint /research avec le graphe LangGraph mocké,
pour ne dépendre ni de Groq ni de Tavily lors du `pytest` (rapide, pas de
coût, pas de flakiness réseau).
"""
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from app.main import app

client = TestClient(app)


def _fake_ai_message_with_answer(answer: str, references=None):
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": "ReviseAnswer",
                "id": "call_1",
                "args": {
                    "answer": answer,
                    "reflection": {"missing": "rien", "superfluous": "rien"},
                    "search_queries": [],
                    "references": references or ["[1] https://exemple.com"],
                },
            }
        ],
    )


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_research_endpoint_returns_final_answer(monkeypatch):
    fake_graph = MagicMock()
    fake_graph.invoke.return_value = [
        _fake_ai_message_with_answer("Réponse finale test")
    ]
    app.state.graph = fake_graph

    response = client.post("/research", json={"question": "Quel est le marché du CRM en 2026 ?"})

    assert response.status_code == 200
    body = response.json()
    assert body["final_answer"] == "Réponse finale test"
    assert body["iterations"] == 1


def test_research_endpoint_rejects_short_question():
    response = client.post("/research", json={"question": "hi"})
    assert response.status_code == 422
