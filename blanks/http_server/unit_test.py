import pytest
from fastapi.testclient import TestClient
from .example import create_app
from .example import Settings
from .example import router
from .example import UserModel
from polyfactory.factories.pydantic_factory import ModelFactory

@pytest.fixture(scope="session")
def test_settings():
    return Settings()


@pytest.fixture(scope="session")
def test_client(test_settings):
    app = create_app(test_settings, routers=[router])
    return TestClient(app)



class UserModelFactory(ModelFactory[UserModel]):
    pass


class TestApi:
    @pytest.fixture()
    def user(self):
        return UserModelFactory.build()

    def test_read_users(self, test_client):
        response = test_client.get("api/users")

        assert response.status_code == 200, response.content

        data = response.json()
        assert data == [{"username": "Rick"}, {"username": "Morty"}]

    def test_create_user(self, user, test_client):
        response = test_client.post("api/users", content=user.model_dump_json())

        assert response.status_code == 201, response.content

        data = response.json()

        assert data == user.model_dump(mode="json")