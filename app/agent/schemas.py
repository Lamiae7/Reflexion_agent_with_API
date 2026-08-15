"""
Modèles Pydantic utilisés comme "tools" liés au LLM afin de forcer une
sortie structurée (function calling).
"""
from typing import List

from pydantic import BaseModel, Field


class Reflection(BaseModel):
    """Auto-critique structurée de la réponse générée par le modèle."""

    missing: str = Field(description="Quelles informations manquent dans la réponse")
    superfluous: str = Field(description="Quelles informations sont superflues")


class AnswerQuestion(BaseModel):
    """Sortie structurée du premier passage (Responder) : réponse initiale,
    auto-critique et requêtes de recherche pour combler les lacunes."""

    answer: str = Field(description="Réponse principale à la question")
    reflection: Reflection = Field(description="Auto-critique de la réponse")
    search_queries: List[str] = Field(
        description="Requêtes de recherche pour approfondir la réponse"
    )


class ReviseAnswer(AnswerQuestion):
    """Sortie structurée du Revisor : reprend AnswerQuestion et ajoute les
    références utilisées pour étayer la réponse révisée."""

    references: List[str] = Field(
        description="Citations/sources ayant motivé la réponse révisée"
    )
