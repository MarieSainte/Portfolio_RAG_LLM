# Portfolio RAG — Chatbot IA

[![Build & Deploy](https://github.com/MarieSainte/Portfolio_RAG_LLM/actions/workflows/deploy.yml/badge.svg)](https://github.com/MarieSainte/Portfolio_RAG_LLM/actions/workflows/deploy.yml)
[![PR Checks](https://github.com/MarieSainte/Portfolio_RAG_LLM/actions/workflows/pr-checks.yml/badge.svg)](https://github.com/MarieSainte/Portfolio_RAG_LLM/actions/workflows/pr-checks.yml)

Portfolio interactif d'ingénieur IA doté d'un **chatbot RAG** (Retrieval-Augmented Generation) capable de répondre aux recruteurs à partir d'une base de projets réels — avec citations et **zéro hallucination**. Pipeline de retrieval à deux étages (recherche dense + reranking cross-encoder), génération via Mistral AI, orchestration **LangChain**, et une **CI/CD** complète (build → gate qualité **Ragas** → déploiement).

---

## ✨ Fonctionnalités

- **Chatbot RAG multi-tours** ancré sur les données : recherche sémantique, mémoire de conversation, réponses sourcées avec liens GitHub.
- **Retrieval à deux étages** : recherche dense (ChromaDB) élargie, puis **reranking cross-encoder multilingue** sur CPU pour la précision.
- **Orchestration LangChain** (LCEL) entièrement traçable via **LangSmith**.
- **Évaluation automatisée** avec **Ragas** (faithfulness, context precision/recall, answer relevancy) en **gate bloquante** de CI.
- **Tests unitaires** (pytest) et **rate-limiting** de l'API pour protéger les crédits LLM.
- **Frontend Angular 21** bilingue (i18n FR/EN), thème clair/sombre.
- **Déploiement continu robuste** : gate tests + qualité → images Docker sur GHCR (épinglées par SHA) → déploiement SSH avec healthchecks et **rollback**.

## 🏗️ Architecture

```mermaid
flowchart LR
    U[Navigateur] -->|HTTP :8080| F[Frontend Angular<br/>nginx]
    F -->|/api/*| B[Backend FastAPI]
    B -->|retrieve k=10| C[(ChromaDB<br/>embeddings)]
    B -->|rerank top-3| R[Cross-Encoder<br/>CPU]
    B -->|génération| M[Mistral AI]
    B -.->|tracing| LS[LangSmith]
```

Le frontend nginx sert l'app Angular **et** proxifie `/api` vers le backend : un seul port exposé, pas de souci de CORS.

## 🧩 Stack technique

| Domaine | Technologies |
|---|---|
| **Frontend** | Angular 21, TypeScript, SCSS, RxJS, ngx-translate |
| **Backend** | Python 3.10, FastAPI, Pydantic, Uvicorn |
| **RAG / LLM** | LangChain, Mistral AI, ChromaDB, SQLite FTS5 (BM25), Sentence-Transformers, Cross-Encoder reranker |
| **Observabilité** | LangSmith (tracing) |
| **Évaluation** | Ragas (LLM-as-a-judge) |
| **Infra / CI-CD** | Docker, Docker Compose, GitHub Actions, GHCR |

## 🔎 Pipeline RAG

1. **Indexation** — le CSV des projets est découpé (`RecursiveCharacterTextSplitter`, `CHUNK_SIZE` configurable) puis indexé au démarrage dans **deux** stores : ChromaDB (vecteurs `all-MiniLM-L6-v2`) et un index lexical SQLite FTS5.
2. **Recherche hybride** — en parallèle, recherche **dense** (Chroma, *k=10*, proximité sémantique) et **lexicale** (FTS5/BM25, *k=10*, correspondance exacte de mots-clés : technos, acronymes). Les candidats des deux sources sont fusionnés et dédupliqués.
3. **Reranking** — un cross-encoder multilingue (`mmarco-mMiniLMv2-L12`) réordonne l'ensemble fusionné et ne garde que les *top-5* (précision accrue, tourne sur CPU).
4. **Génération** — Mistral AI répond en s'appuyant **uniquement** sur ce contexte (prompt système strict anti-hallucination).

## 🗂️ Journal des interactions

Chaque échange (`/chat`) est enregistré dans une base **SQLite persistante** avec un index **FTS5** (recherche plein-texte BM25 sur questions + réponses). Utile pour analyser ce que demandent les visiteurs.

Consultation via un endpoint d'administration, **désactivé par défaut** : il ne s'active que si `ADMIN_TOKEN` est défini, et exige alors l'en-tête `X-Admin-Token`.

```bash
# Dernières interactions
curl -H "X-Admin-Token: $ADMIN_TOKEN" http://localhost:8080/api/admin/interactions
# Recherche plein-texte (FTS5)
curl -H "X-Admin-Token: $ADMIN_TOKEN" "http://localhost:8080/api/admin/interactions?q=fine-tuning"
```

La base vit dans `/app/data` (bind mount `./data` en prod) : elle **survit au redéploiement** et n'est pas effacée par le `down -v` qui reconstruit l'index vectoriel.

## 🚀 Démarrage local

Prérequis : Docker + Docker Compose.

```bash
cp .env.example .env        # renseigner MISTRAL_API_KEY
docker compose up --build
```

- Frontend : http://localhost:8080
- API : http://localhost:8000 · ChromaDB : http://localhost:8001

## 📊 Évaluation (Ragas)

```bash
cd backend
pip install -r requirements-eval.txt
python -m evals.run_ragas
```

Note la chaîne RAG sur un jeu de questions de référence. La CI **échoue** si un score moyen passe sous son seuil (faithfulness ≥ 0.70, autres ≥ 0.60) — voir [`backend/evals/`](backend/evals/).

## 🔄 CI/CD (GitHub Actions)

Workflows réutilisables ([`_tests.yml`](.github/workflows/_tests.yml), [`_ragas.yml`](.github/workflows/_ragas.yml)) partagés entre les PR et le déploiement (DRY) :

| Workflow | Déclencheur | Pipeline |
|---|---|---|
| [`pr-checks.yml`](.github/workflows/pr-checks.yml) | Pull Request | tests (pytest) → gate Ragas |
| [`deploy.yml`](.github/workflows/deploy.yml) | push sur `main` | tests → gate Ragas → build+push GHCR → déploiement SSH → healthcheck |

- **Déploiement gaté** : on ne build/déploie que si les tests **et** la qualité RAG passent.
- **Images épinglées par SHA** + healthchecks compose → déploiement traçable et vérifié.
- **Rollback** : `deploy.yml` en `workflow_dispatch` avec l'entrée `rollback_sha` redéploie une image antérieure sans rebuild.

Secrets requis : `MISTRAL_API_KEY`, `SSH_PRIVATE_KEY`, `SERVER_HOST`, `SERVER_USER` (+ `LANGSMITH_API_KEY` optionnel).

## 📁 Structure

```
.
├── backend/            # API FastAPI + pipeline RAG LangChain
│   ├── app/            # config, controllers, services (rag, mistral), schemas
│   └── evals/          # évaluation Ragas + dataset
├── frontend/           # application Angular 21
├── docker-compose.yml       # dev (build local)
├── docker-compose.prod.yml  # prod (images GHCR)
└── .github/workflows/       # CI/CD
```
