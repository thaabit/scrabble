from typing import TYPE_CHECKING, List
from datetime import datetime
from sqlmodel import Field, or_, select, Relationship, Session, text
from models.SQLModelBase import SQLModelBase
from models.Game import Game

if TYPE_CHECKING:
    from .models.Game import Game

class UserBase(SQLModelBase):
    username: str = Field(unique=True)
    created: datetime | None = Field(default_factory=datetime.utcnow)

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pwhash: str = Field()
    trays: List["GameUser"] = Relationship()
    avatar: str | None = Field(default='')
    name: str | None = Field(default='')
    username: str

    def turn_count(self, session):
        sql = f"""
            SELECT g.id, gu.tray, gu.ack_end
              FROM game_user gu
              JOIN game g ON g.id = gu.game_id
             WHERE gu.username = :un
               AND g.finished='0000-00-00 00:00:00'
               """
        games = session.execute(text(sql), params={"un": self.username}).mappings().all()
        turns = [game['id'] for game in games if session.get(Game, game['id']).whose_turn() == self.username]
        return turns

class UserCreate(UserBase):
    password: str

class UserUpdate(SQLModelBase):
    name: str
    password: str | None = None

