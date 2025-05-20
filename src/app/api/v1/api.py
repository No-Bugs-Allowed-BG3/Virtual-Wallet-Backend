"""REST API endpoints"""

from fastapi import APIRouter

from app.api.v1.routes.user_route import router as user_route

api_router = APIRouter()

api_router.include_router(user_route, prefix="/users", tags=["Users"])
