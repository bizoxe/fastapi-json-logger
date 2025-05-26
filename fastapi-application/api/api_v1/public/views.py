import logging

from fastapi import APIRouter

router = APIRouter(
    tags=["Public"],
)

logger = logging.getLogger(__name__)


@router.get("")
async def greeting() -> dict[str, str]:
    logger.info("Info message")

    return {"message": "Hello world from FastAPI app!"}
