from datetime import datetime
from sqlmodel import Field
from models.SQLModelBase import SQLModelBase

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
