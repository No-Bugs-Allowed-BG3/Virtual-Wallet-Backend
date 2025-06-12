from contextlib import asynccontextmanager
from urllib.parse import urljoin
from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.api import api_router
from app.persistence.db import initialize_database
from fastapi.middleware.cors import CORSMiddleware


def _create_app() -> FastAPI:
    app_ = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=urljoin(settings.API_V1_STR, "openapi.json"),
        version=settings.VERSION,
        docs_url="/docs",
        lifespan=lifespan,
    )
    origins = [
        "http://192.168.10.139:3000",
        "https://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    app_.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app_.include_router(
        api_router,
        prefix=settings.API_V1_STR,
    )
    return app_


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle the lifespan of the FastAPI application.
    """
    await initialize_database()
    yield


app = _create_app()
