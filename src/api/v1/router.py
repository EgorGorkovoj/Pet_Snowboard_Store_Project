from fastapi import APIRouter

from src.api.auth import user_router
from src.api.v1.endpoints import product_router

main_router = APIRouter()

main_router.include_router(product_router, tags=['Товары и категории'])
main_router.include_router(user_router)
