import respx
import pytest
import uuid
import httpx
from polyfactory.factories.pydantic_factory import ModelFactory

from .example import MyClient
from .example import MyModel
from .main import Settings


BASE_URL = f"https://{uuid.uuid4()}.com/"


class MyModelFactory(ModelFactory[MyModel]):
    pass


class TestMyClient:
    @pytest.fixture()
    def api_mock(self):
        mocked_api = respx.mock(base_url=BASE_URL)
        mocked_api.start()
        yield mocked_api
        mocked_api.stop()

    @pytest.fixture()
    async def my_client(self):
        client = MyClient(Settings(base_url=BASE_URL))
        await client.startup()
        yield client
        await client.shutdown()
    
    @pytest.fixture()
    def my_model_instance(self):
        return MyModelFactory.build()

    @pytest.fixture()
    def get_smth_mock(self, api_mock, my_model_instance):
        api_mock.get("/smth").mock(
            return_value=httpx.Response(
                200,
                content=my_model_instance.model_dump_json(),
            )
        )

    @pytest.fixture()
    def create_smth_mock(self, api_mock, my_model_instance):
        api_mock.post("/smth").mock(
            return_value=httpx.Response(
                201,
                content=my_model_instance.model_dump_json(),
            )
        )

    @pytest.mark.usefixtures("get_smth_mock")
    async def test_get_smth(self, get_smth_mock, my_client, my_model_instance):
        response = await my_client.get_smth()

        assert response == my_model_instance

    @pytest.mark.usefixtures("create_smth_mock")
    async def test_create_smth(self, my_client, my_model_instance):
        response = await my_client.create_smth(my_model_instance)

        assert response == my_model_instance
