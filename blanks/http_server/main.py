from fastapi import FastAPI
from pydantic_settings import BaseSettings
from fastapi import APIRouter


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 5000

    @property
    def base_url(self) -> str:
        return f"{self.host}:{self.port}"


def create_app(settings: Settings, routers: list[APIRouter]):
    app = FastAPI()

    for router in routers:
        app.include_router(router)

    return app

