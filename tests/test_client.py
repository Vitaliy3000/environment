import datetime
from blanks import client
from pydantic import BaseModel


class MyModel(BaseModel):
    id: int
    message: str
    timestamp: datetime.datetime


class MyClient(client.BaseHttpClient):
    async def get_smth(self) -> MyModel:
        response = self._client.get("/smth")

        return self._process_response(response, model=MyModel)

    async def create_smth(self, data: MyModel) -> MyModel:
        response = await self._client.post("/smth", json=data.model_dump())

        return self._process_response(response, model=MyModel)


class TestMyClient:
    def test_get_smth(self):
        pass

    def test_create_smth(self):
        pass
