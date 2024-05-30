import pytest
from testcontainers.postgres import PostgresContainer
from .main import Settings
from .main import metadata
from .example import UserRepository
from .example import UserModel
from sqlalchemy.ext.asyncio import create_async_engine
from polyfactory.factories.pydantic_factory import ModelFactory
import uuid

class UserModelFactory(ModelFactory[UserModel]):
    pass


@pytest.fixture(scope="session", autouse=True)
def container():
    instance = PostgresContainer(
        username="postgres",
        password="postgres",
        dbname="postgres",
    )

    with instance:
        yield instance


@pytest.fixture(scope="session")
def test_settings(container) -> Settings:
    return Settings(
        host=container.get_container_host_ip(),
        port=container.get_exposed_port(container.port),
        username=container.username,
        password=container.password,
        dbname=container.dbname,
    )


@pytest.fixture(scope="function", autouse=True)
async def engine(test_settings):
    engine = create_async_engine(test_settings.url)

    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(metadata.drop_all)


@pytest.fixture
async def user_repository(test_settings):
    repo = UserRepository(test_settings)
    await repo.startup()
    yield repo
    await repo.shutdown()


class TestUserRepository:
    async def test_crud(self, user_repository) -> None:
        fetched_users = await user_repository.get_all()
        assert len(fetched_users) == 0

        user = UserModelFactory.build()
        created_user = await user_repository.create(user)
        assert user == created_user

        fetched_user = await user_repository.get_one_or_none(id=user.id)
        assert user == fetched_user

        other_user = UserModelFactory.build()
        created_other_user = await user_repository.create(other_user)
        fetched_users = await user_repository.get_all()

        assert sorted(fetched_users, key=lambda x: x.id) == sorted([user, other_user], key=lambda x: x.id)

        user.name = str(uuid.uuid4())
        updated_user = await user_repository.update(user)
        assert user == updated_user

        fetched_user = await user_repository.get_one_or_none(id=user.id)
        assert user == fetched_user

        deleted_user = await user_repository.delete(id=user.id)
        assert user == deleted_user

        fetched_user = await user_repository.get_one_or_none(id=user.id)
        assert fetched_user is None

        fetched_users = await user_repository.get_all()
        assert len(fetched_users) == 1
        assert fetched_users[0] == other_user
