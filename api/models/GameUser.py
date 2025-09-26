from typing import TYPE_CHECKING, Optional
from models.SQLModelBase import SQLModelBase
from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from .models.Game import Game

class GameUser(SQLModelBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.id")
    username: str = Field(foreign_key="user.username")
    tray: str | None = Field(default='')
    game: Optional["Game"] = Relationship(back_populates = "trays")
    __tablename__ = "game_user"
