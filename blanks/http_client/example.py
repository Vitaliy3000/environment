import datetime
from .main import BaseHttpClient
from pydantic import BaseModel


class MyModel(BaseModel):
    id: int
    message: str
    timestamp: datetime.datetime


class MyClient(BaseHttpClient):
    async def get_smth(self) -> MyModel:
        response = await self.client.get("/smth")

        return self._process_response(response, model=MyModel)

    async def create_smth(self, data: MyModel) -> MyModel:
        response = await self.client.post("/smth", json=data.model_dump_json())

        return self._process_response(response, model=MyModel)

