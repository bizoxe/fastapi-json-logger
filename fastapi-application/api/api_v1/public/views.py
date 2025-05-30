import logging

from fastapi import APIRouter
from pydantic import (
    BaseModel,
    EmailStr,
)

router = APIRouter(
    tags=["Public"],
)

logger = logging.getLogger(__name__)


class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


@router.get("")
async def greeting() -> dict[str, str]:
    logger.info("Info message")

    return {"message": "Hello world from FastAPI app!"}


@router.post("/user")
async def get_user_data(user: User) -> User:
    logger.info(
        "User data: first_name=%s, last_name=%s, email=%s",
        user.first_name,
        user.last_name,
        user.email,
    )
    return user
