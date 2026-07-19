from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.controllers.chat_controller import router as chat_router
import uvicorn

from app.core.lifespan import lifespan

def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Routers
    app.include_router(chat_router)

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
