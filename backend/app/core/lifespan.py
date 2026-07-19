import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup LOGIC
    from app.services.rag_service import rag_service

    # experience.csv est dans backend/app/data, ce fichier dans backend/app/core
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(os.path.dirname(current_dir), "data", "experience.csv")

    logger.info("startup: indexing experience data", extra={"context": {"path": csv_path}})
    try:
        rag_service.index_csv(csv_path)
    except Exception:
        logger.exception("startup: failed to index CSV")

    yield

    # Shutdown LOGIC
    logger.info("shutdown: cleaning up resources")
