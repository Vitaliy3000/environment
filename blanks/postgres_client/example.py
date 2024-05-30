import sqlalchemy as sa
from pydantic import BaseModel
from pydantic import ConfigDict

import datetime
from .main import metadata
from .main import Repository


user_table = sa.Table(
    "user",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String, nullable=False),
    sa.Column("timestamp", sa.DateTime, nullable=False),
)


class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    timestamp: datetime.datetime


class UserRepository(Repository[UserModel]):
    model = UserModel
    table = user_table