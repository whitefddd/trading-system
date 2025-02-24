from fastapi import APIRouter
from . import endpoints, auth

router = APIRouter()
router.include_router(endpoints.router)
router.include_router(auth.router, prefix="/auth", tags=["auth"]) 