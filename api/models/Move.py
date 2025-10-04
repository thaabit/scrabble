from typing import TYPE_CHECKING, Optional
from models.SQLModelBase import SQLModelBase
from sqlmodel import Field, Relationship, Column
from enum import StrEnum, Enum
import re

if TYPE_CHECKING:
    from .models.Game import Game

class MoveType(StrEnum):
    PASS = 'pass'
    PLAY = 'play'
    CHALLENGE = 'challenge'
    EXCHANGE = 'exchange'

class Move(SQLModelBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.id")
    username: str = Field(foreign_key="user.username")
    type: str | None = Field(default='play')
    data: str
    main_word: Optional[str] = ''
    rack: Optional[str] = ''
    score: int | None = 0
    game: Optional["Game"] = Relationship(back_populates="moves")

    def tiles(self):
        if self.type != 'play': return []
        if not self.data or self.data == '': raise Exception(f"Move must have at least one letter")
        tiles = [x for x in self.data.split("::")]
        out = []

        for t in tiles:
            parts = t.split(':')
            if len(parts) != 3: raise Exception(f"Invalid tile: {self.data}")
            out.append((parts[0].upper(), (int(parts[1]), int(parts[2]))))
        return out

    def coords(self):
        coords = dict([(t[1], t[0]) for t in self.tiles()])
        return coords
