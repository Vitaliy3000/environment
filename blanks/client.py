import typing
import httpx
from pydantic import HttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_url: HttpUrl


class BaseHttpClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self.__client = None

    @property
    def _client(self):
        if self._client is None:
            raise RuntimeError("Client not initialized")
        
        self.__client = typing.cast(httpx.AsyncClient, self.__client)
        return self.__client

    async def startup(self) -> None:
        self._client = httpx.AsyncClient(base_url=self._settings.base_url)

    async def shutdown(self) -> None:
        self._client.close()
