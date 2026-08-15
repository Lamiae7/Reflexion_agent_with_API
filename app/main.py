"""
Point d'entrée de l'application FastAPI.

Le graphe LangGraph est construit une seule fois au démarrage (event
`startup`) et stocké dans `app.state.graph`, plutôt que d'être reconstruit
à chaque requête — évite de recréer inutilement les clients LLM/HTTP.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent.graph import build_graph
from app.api.routes import router
from app.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

import logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Construction du graphe Reflexion...")
    app.state.graph = build_graph()
    logger.info(
        "Graphe prêt. max_iterations=%s model=%s",
        settings.max_iterations,
        settings.model_name,
    )
    yield


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=(
        "API exposant un agent Reflexion qui produit des briefs "
        "de recherche factuels et sourcés : réponse initiale, auto-critique, "
        "recherche web, puis révision citée."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
