from fastapi import APIRouter

router = APIRouter(
    tags=["Public"],
)


@router.get("")
def greeting():

    return {"message": "Hello world from FastAPI app!"}
