"""
Outil de recherche web (Tavily) utilisé par le node `execute_tools` du graphe.
"""
from langchain_tavily import TavilySearch

from app.config import get_settings


def get_search_tool() -> TavilySearch:
    """Instancie l'outil de recherche Tavily à partir des settings."""
    settings = get_settings()
    return TavilySearch(max_results=settings.tavily_max_results, tavily_api_key=settings.tavily_api_key)
