from fastapi import APIRouter

from src.api.user import router as user_router
from src.api.staff import router_staff as staff_router
main_router = APIRouter()

main_router.include_router(user_router)
main_router.include_router(staff_router)