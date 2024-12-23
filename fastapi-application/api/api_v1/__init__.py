from fastapi import APIRouter

from api.api_v1.public.views import router as public_router
from core.config import settings

router = APIRouter(
    prefix=settings.api.v1.prefix,
)
router.include_router(
    public_router,
    prefix=settings.api.v1.public,
)
