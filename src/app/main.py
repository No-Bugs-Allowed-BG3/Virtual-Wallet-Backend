from contextlib import asynccontextmanager
from urllib.parse import urljoin
from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.api import api_router
from app.persistence.db import initialize_database
from app.persistence.initial_data import load_initial_currencies


def _create_app() -> FastAPI:
    app_ = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=urljoin(settings.API_V1_STR, "openapi.json"),
        version=settings.VERSION,
        docs_url="/docs",
        lifespan=lifespan,
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

    await load_initial_currencies()
    yield


app = _create_app()
