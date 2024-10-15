from typing import TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, or_, select
from models.SQLModelBase import SQLModelBase

if TYPE_CHECKING:
    from .models.Game import Game

class UserBase(SQLModelBase):
    username: str = Field(unique=True)
    created: datetime | None = Field(default_factory=datetime.utcnow)

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pwhash: str = Field()

class UserCreate(UserBase):
    password: str

class UserUpdate(SQLModelBase):
    username: str | None = None
    password: str | None = None
