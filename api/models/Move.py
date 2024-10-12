from typing import TYPE_CHECKING, Optional
from models.SQLModelBase import SQLModelBase
from sqlmodel import Field, Relationship
import re

if TYPE_CHECKING:
    from .models.Game import Game

class Move(SQLModelBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.id")
    user: str = Field(foreign_key="user.username")
    type: str | None = Field(default='play')
    move: str
    score: int | None = 0
    game: Optional["Game"] = Relationship(back_populates="moves")

    def tiles(self):
        tiles = [x for x in self.move.split("::")]
        out = []
        for t in tiles:
            parts = t.split(':')
            out.append((parts[0].upper(), (int(parts[1]), int(parts[2]))))
        return out

    def coords(self):
        coords = dict([(t[1], t[0]) for t in self.tiles()])
        return coords
