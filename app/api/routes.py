"""
Routes HTTP de l'API. Le graphe LangGraph est construit une seule fois au
démarrage (voir app/main.py) et réutilisé à chaque requête pour éviter de
recréer les chains/clients LLM à chaque appel.
"""
import logging
import time

from fastapi import APIRouter, HTTPException, Request

from app.api.schemas import RevisionStep, ResearchRequest, ResearchResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", tags=["monitoring"])
def health_check():
    """Endpoint de liveness/readiness pour les orchestrateurs (Docker, Render...)."""
    return {"status": "ok"}


@router.post("/research", response_model=ResearchResponse, tags=["agent"])
def run_research(payload: ResearchRequest, request: Request):
    """Exécute la boucle Reflexion complète sur la question fournie et
    renvoie la réponse finale ainsi que le détail de chaque itération
    (utile pour l'observabilité / le debug côté client)."""
    graph = request.app.state.graph

    started_at = time.perf_counter()
    try:
        messages = graph.invoke(payload.question)
    except Exception as exc:  # 
        logger.exception("Échec de l'exécution du graphe Reflexion")
        raise HTTPException(
            status_code=502,
            detail=f"L'agent de recherche a échoué : {exc}",
        ) from exc
    elapsed = time.perf_counter() - started_at
    logger.info("Requête traitée en %.2fs (%d messages)", elapsed, len(messages))

    steps: list[RevisionStep] = []
    for i, msg in enumerate(messages):
        if not getattr(msg, "tool_calls", None):
            continue
        for tool_call in msg.tool_calls:
            args = tool_call.get("args", {})
            if "answer" not in args:
                continue
            reflection = args.get("reflection", {}) or {}
            steps.append(
                RevisionStep(
                    step=len(steps) + 1,
                    answer=args["answer"],
                    missing=reflection.get("missing"),
                    superfluous=reflection.get("superfluous"),
                    search_queries=args.get("search_queries", []),
                    references=args.get("references", []),
                )
            )

    if not steps:
        raise HTTPException(
            status_code=502, detail="L'agent n'a produit aucune réponse exploitable."
        )

    final_step = steps[-1]
    return ResearchResponse(
        question=payload.question,
        final_answer=final_step.answer,
        final_references=final_step.references,
        iterations=len(steps),
        steps=steps,
    )
