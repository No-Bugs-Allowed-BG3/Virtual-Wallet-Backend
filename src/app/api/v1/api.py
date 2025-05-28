"""REST API endpoints"""

from fastapi import APIRouter

from app.api.v1.routes.user_route import router as user_route
from api.v1.routes.tokens_router import token_router

api_router = APIRouter()

api_router.include_router(user_route, prefix="/users", tags=["Users"])
api_router.include_router(token_router,prefix="/tokens",tags=["Auth/Login"])
