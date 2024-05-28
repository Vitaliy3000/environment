import typing
import httpx
from pydantic import HttpUrl
from pydantic_settings import BaseSettings
from pydantic import BaseModel


Model = typing.TypeVar("Model", bound=BaseModel)


class Settings(BaseSettings):
    base_url: HttpUrl


class BaseHttpClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Client not initialized")

        self._client = typing.cast(httpx.AsyncClient, self._client)
        return self._client

    async def startup(self) -> None:
        self._client = httpx.AsyncClient(base_url=str(self._settings.base_url))

    async def shutdown(self) -> None:
        await self._client.aclose()

    def _process_response(self, response: httpx.Response, *, model: type[Model],):
        response.raise_for_status()

        return model.model_validate_json(response.content)
