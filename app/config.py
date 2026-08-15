"""
Configuration centralisée de l'application.

Toutes les valeurs sensibles (clés API) sont lues depuis l'environnement
(.env en local, variables d'environnement en production).
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- LLM ---  #
    groq_api_key: str  
    model_name: str  
    llm_temperature: float  

    # --- Recherche web ---
    tavily_api_key: str  
    tavily_max_results: int

    # --- Comportement de l'agent Reflexion ---
    max_iterations: int = 2  # nombre de cycles critique -> recherche -> révision

    # --- API ---
    api_title: str  
    api_version: str  
    log_level: str  

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Instancie les settings une seule fois (cache) pour éviter de
    relire l'environnement à chaque appel."""
    return Settings()
