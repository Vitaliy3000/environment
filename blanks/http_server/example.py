from fastapi import APIRouter
from fastapi import Response
import datetime
from .main import create_app
from .main import Settings
import uvicorn
from pydantic import BaseModel

router = APIRouter(prefix="/api")


class UserModel(BaseModel):
    id: int
    name: str
    timestamp: datetime.datetime


@router.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.post("/users/", status_code=201, tags=["users"])
async def create_user(user: UserModel) -> UserModel:
    return user


if __name__ == "__main__":
    settings = Settings()

    app = create_app()

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
    )
