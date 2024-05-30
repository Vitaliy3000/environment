import typing
import sqlalchemy as sa
from contextvars import ContextVar
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncTransaction
from contextlib import asynccontextmanager
from pydantic import BaseModel
from pydantic_settings import BaseSettings


metadata = sa.MetaData()


Model = typing.TypeVar("Model", bound=BaseModel)

class Settings(BaseSettings):
    host: str
    port: int
    username: str
    password: str
    dbname: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}"


class Repository(typing.Generic[Model]):
    model: type[Model]
    table: sa.Table

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._context_transaction = ContextVar("transaction")
        self._engine: AsyncEngine | None = None

    async def startup(self):
        self._engine = create_async_engine(self._settings.url)

    async def shutdown(self):
        await self.engine.dispose()

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise RuntimeError("Engine wasn't initialized")

        return self._engine

    async def get_one_or_none(self, id: typing.Any) -> Model | None:
        stmt = sa.select(self.table).where(self.table.c.id == id)

        async with self._transaction() as transaction:
            cursor = await transaction.connection.execute(stmt)
            row = cursor.fetchone()

        if row is None:
            return None

        return self.model.model_validate(row)

    async def get_all(self) -> list[Model]:
        stmt = sa.select(self.table)

        async with self._transaction() as transaction:
            cursor = await transaction.connection.execute(stmt)
            rows = cursor.fetchall()
        
        return [self.model.model_validate(row) for row in rows]

    async def create(self, model) -> Model:
        data = model.model_dump()

        stmt = (
            sa.insert(self.table).
            values(data)
            .returning(self.table)
        )

        async with self._transaction() as transaction:
            cursor = await transaction.connection.execute(stmt)
            row = cursor.fetchone()

        return self.model.model_validate(row)

    async def update(self) -> Model:
        pass

    async def delete(self, id: typing.Any) -> Model:
        stmt = (
            sa.delete(self.table)
            .where(self.table.c.id == id)
            .returning()
        )
    
        async with self._transaction() as transaction:
            await transaction.connection.execute(stmt)

        return 
    
    @asynccontextmanager
    async def _transaction(self) -> AsyncTransaction:
        try:
            yield self._context_transaction.get()
        except LookupError:
            async with self.engine.connect() as connection:
                async with connection.begin() as transaction:
                    yield transaction

    @asynccontextmanager
    async def create_transacion(self) -> AsyncTransaction:
        try:
            self._context_transaction.get()
        except LookupError:
            pass
        else:
            raise RuntimeError("Nested transactions are forbidden")

        async with self.engine.connect() as connection:
            async with connection.begin() as transaction:
                self._context_transaction.set(transaction)
                try:
                    yield
                except Exception:
                    transaction.rollback()
                    raise
                else:
                    transaction.commit()
                finally:
                    self._context_transaction.reset()
