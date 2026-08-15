# Market Research Copilot — Reflexion Agent

API FastAPI exposant un **agent Reflexion** (pattern issu du papier [Reflexion:
Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366),
implémenté avec [LangGraph](https://langchain-ai.github.io/langgraph/)) qui produit
des **briefs de recherche factuels et sourcés** sur une entreprise, un marché, une
technologie ou une évolution réglementaire — pensé pour des consultants, analystes,
sales ou product managers qui ont besoin d'une synthèse rapide et fiable plutôt
que d'une réponse LLM "premier jet".

> déployable : API, config par variables d'environnement, tests, Docker,
> déploiement cloud.

## Pourquoi Reflexion plutôt qu'un simple appel LLM ?

Un LLM interrogé une seule fois répond souvent avec des informations datées ou
incomplètes. Cet agent boucle sur 3 étapes :

```
┌───────────┐      ┌────────────────┐      ┌──────────┐
│  Responder │ ───▶ │ execute_tools   │ ───▶ │ Revisor  │──┐
│ (1er jet + │      │ (recherche web  │      │ (réponse │  │
│  critique) │      │  Tavily sur les │      │  sourcée)│  │
└───────────┘      │  lacunes)       │      └──────────┘  │
                    └────────────────┘            │        │
                                                    ▼        │
                                          nb itérations >= N
                                             non ──────────┘ (relance execute_tools)
                                             oui → fin, réponse finale
```

1. **Responder** : génère une première réponse, s'auto-critique ("qu'est-ce qui
   manque, qu'est-ce qui est superflu ?") et propose des requêtes de recherche.
2. **execute_tools** : exécute ces requêtes via l'API Tavily.
3. **Revisor** : réécrit la réponse en intégrant les résultats de recherche,
   avec citations numérotées, jusqu'à `MAX_ITERATIONS` cycles.

Le gain de qualité entre la réponse du `Responder` (étape 1) et celle du
`Revisor` (étape finale) est directement observable via le champ `steps` de la
réponse API — c'est la valeur mesurable du pattern.

## Architecture du projet

```
reflexion-agent/
├── app/
│   ├── main.py              # App FastAPI + lifespan (construction du graphe)
│   ├── config.py             # Settings (pydantic-settings, lecture .env)
│   ├── agent/
│   │   ├── schemas.py        # Sorties structurées du LLM (tool calling)
│   │   ├── prompts.py        # Prompts Responder / Revisor
│   │   ├── tools.py          # Wrapper recherche web (Tavily)
│   │   ├── chains.py         # LLM + prompt + tool binding
│   │   └── graph.py          # Graphe LangGraph (nodes + boucle conditionnelle)
│   └── api/
│       ├── schemas.py        # Contrats HTTP (requête/réponse)
│       └── routes.py         # Endpoints /research, /health
├── tests/                    # Tests unitaires + API (mockés, sans appel réseau)
├── Dockerfile
├── docker-compose.yml
├── render.yaml                # Déploiement Render (free tier)
├── requirements.txt
└── .env.example
```
 

## Stack

- **FastAPI** — API HTTP, validation, doc Swagger auto-générée
- **LangGraph** — orchestration de la boucle Reflexion (state machine)
- **LangChain / langchain-groq** — abstraction LLM + tool calling structuré
- **Groq** (Llama 3.3 70B) — inférence LLM rapide et gratuite
- **Tavily** — recherche web pour l'étape de révision
- **Docker** — containerisation
- **Render** — déploiement (free tier, config dans `render.yaml`)

## Lancer en local

### Avec Docker (recommandé)

```bash
cp .env.example .env
# renseigner GROQ_API_KEY et TAVILY_API_KEY dans .env
# clés gratuites : https://console.groq.com/keys et https://app.tavily.com (ce dernier pour la recherche en ligne)

docker compose up --build
```

L'API est disponible sur `http://localhost:8000`, doc interactive sur
`http://localhost:8000/docs`.

### Sans Docker en lab

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # puis renseigner les clés

uvicorn app.main:app --reload
```

### Tests

```bash
pytest tests/ -v
```
 

## Utilisation de l'API

### `POST /research`

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"question": "Quelle est la position concurrentielle de Mistral AI face à OpenAI en 2026 ?"}'
```

Réponse (extrait) :

```json
{
  "question": "Quelle est la position concurrentielle de Mistral AI face à OpenAI en 2026 ?",
  "final_answer": "...",
  "final_references": ["[1] https://...", "[2] https://..."],
  "iterations": 2,
  "steps": [
    {"step": 1, "answer": "...", "missing": "...", "superfluous": "...", "search_queries": ["..."]},
    {"step": 2, "answer": "...", "references": ["..."]}
  ]
}
```

Le champ `steps` expose tout le raisonnement intermédiaire (première réponse,
auto-critique, requêtes de recherche, réponse finale sourcée) — 

### `GET /health`

Endpoint de liveness pour Docker/Render.

## Sécurité

- `.env` est dans `.gitignore`  
  

## Limites connues / axes d'amélioration

- Pas de cache : deux requêtes identiques relancent tout le pipeline (LLM +
  recherche web) — un cache Redis sur `question -> réponse` serait le premier
  gain de perf/coût en prod.
- Pas de rate limiting sur l'API — à ajouter avant une exposition publique
  large (ex. `slowapi`).
- Pas de CI/CD ni de tracing (LangSmith) dans cette version 
- Le modèle Groq gratuit a des limites de rate/quota .

