"""REST API endpoints"""

from fastapi import APIRouter

from app.api.v1.routes.user_route import router as user_route
from app.api.v1.routes.tokens_router import token_router
from app.api.v1.routes.card_route import router as card_route
from app.api.v1.routes.contact_route import router as contact_route
from app.api.v1.routes.admin_route import router as admin_route
from app.api.v1.routes.categories_router import router as category_router
from app.api.v1.routes.transaction_router import router as transaction_router
from app.api.v1.routes.balance_router import router as balance_router

api_router = APIRouter()

api_router.include_router(user_route, prefix="/users", tags=["Users"])
api_router.include_router(token_router,prefix="/tokens",tags=["Auth/Login"])
api_router.include_router(card_route)
api_router.include_router(contact_route)
api_router.include_router(admin_route)
api_router.include_router(category_router)
api_router.include_router(transaction_router)
api_router.include_router(balance_router)