"""
Schémas Pydantic pour les payloads de l'API HTTP — distincts des schémas
"tools" internes à l'agent (app/agent/schemas.py) pour ne pas coupler le
contrat public de l'API aux détails d'implémentation du graphe.
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Question de recherche (entreprise, marché, techno, réglementation...)",
        examples=[
            "Quelle est la position concurrentielle de Mistral AI face à OpenAI en 2026 ?"
        ],
    )


class RevisionStep(BaseModel):
    step: int
    answer: str
    missing: Optional[str] = None
    superfluous: Optional[str] = None
    search_queries: List[str] = []
    references: List[str] = []


class ResearchResponse(BaseModel):
    question: str
    final_answer: str
    final_references: List[str] = []
    iterations: int
    steps: List[RevisionStep]
