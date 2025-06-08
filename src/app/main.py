from contextlib import asynccontextmanager
from urllib.parse import urljoin
from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.api import api_router
from app.persistence.db import AsyncSessionLocal, initialize_database
from app.persistence.initial_data import create_predefined_categories, load_initial_currencies
from fastapi.middleware.cors import CORSMiddleware

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

    allowed_origins = [
        "http://localhost:3000"
    ]

    app_.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins, 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],   
    )
    return app_


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle the lifespan of the FastAPI application.
    """
    await initialize_database()

    await load_initial_currencies()
    async with AsyncSessionLocal() as session:
        await create_predefined_categories(session)
    # async for session in get_session():
    #     await create_predefined_categories(session)
    yield


app = _create_app()
