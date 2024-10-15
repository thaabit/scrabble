from typing import TYPE_CHECKING, List, Optional
from models.SQLModelBase import SQLModelBase
from datetime import datetime
from sqlmodel import Field, Relationship
import random
import string
import itertools
import re
import numpy as np

if TYPE_CHECKING:
    from .models.Move import Move

bag_start = 'AAAAAAAAABBCCDDDDEEEEEEEEEEEEFFGGGHHIIIIIIIIIJKLLLLMMNNNNNNOOOOOOOOPPQRRRRRRSSSSTTTTTTUUUUVVWWXYYZ??'
value_of_letters = {
    "?": 0,
    "AEILNORSTU":1,
    "DG": 2,
    "BCMP": 3,
    "FHVWY": 4,
    "K": 5,
    "JX": 8,
    "QZ": 10
}
LETTER_VALUES = {}
for key in value_of_letters:
    value = value_of_letters[key]
    for x in key: LETTER_VALUES[x] = value

# (r, c)
TWS_COORDS = [(0,0), (0,7), (0,14), (7,0), (7,14), (14,0), (14,7), (14,14)]
DLS_COORDS = [(0,3), (0,11), (2,6), (2,8), (3,0), (3,7), (3,14), (6,2), (6,6), (6,8), (6,12), (7,3), (7,6), (7,8), (7,11), (8,2), (8,6), (8,8), (8,12), (11,0), (11,7), (11,14), (12,6), (12,8), (14,3), (14,11)]
DWS_COORDS = [(1,1), (1,13), (2,2), (2,12), (3,3), (3,11), (4,4), (4,10), (7,7), (13,1), (13,13), (12,2), (12,12), (11,3), (11,11), (10,4), (10,10)]
TLS_COORDS = [(1,5), (1,9), (5,1), (5,5), (5,9), (5,13), (13,5), (13,9)]
MAX_COLUMN = 14
MAX_ROW = 14

class GameBase(SQLModelBase):
    user_one: str = Field(foreign_key="user.username")
    tray_one: str | None = Field(default='')
    user_two: str = Field(foreign_key="user.username")
    tray_two: str | None = Field(default='')
    created: datetime | None = Field(default_factory=datetime.utcnow)
    finished: datetime | None = Field(default='0000-00-00')
    bag: str | None = Field(default=bag_start)

class Game(GameBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    moves: List["Move"] = Relationship(back_populates = "game")

    def draw(self):

        # check for endgame
        no_more_letters = (self.tray_one == '' or self.tray_two == '') and self.bag == ''
        three_passes = len(self.moves) >= 3 and self.moves[-3].type == 'pass' and self.moves[-2].type == 'pass' and self.moves[-1] == 'pass'
        if no_more_letters or three_passes:
            self.finished = datetime.utcnow()
            return

        # randomize list of letters
        self.bag = ''.join(random.sample(self.bag,len(self.bag)))

        idx1 = 7 - len(self.tray_one)
        self.tray_one += self.bag[0:idx1]
        self.bag = self.bag[idx1:]

        idx2 = 7 - len(self.tray_two)
        self.tray_two += self.bag[0:idx2]
        self.bag = self.bag[idx2:]

        return self


    def first_move(self):
        moves = self.moves
        if not moves: return True
        if not [m.type == 'play' for m in moves]: return True
        return False

    def score(self, user):
        #return sum([int(x.score) for x in list(filter(lambda x: x.user == user, self.moves))])
        return sum([int(x.score) for x in self.moves if x.user == user and x.type == 'play'])

    def valid_move(self, move, username):

        # check for game over
        if self.finished != '0000-00-00': raise Exception("It's game over, man")

        # must be my turn
        if self.whose_turn() != username: raise Exception("It is not your turn")
        tray = self.trays()[username]

        if move.type == 'play':

            play_tiles = move.tiles()
            play_letters = [x[0] for x in play_tiles]
            play_coords = [x[1] for x in play_tiles]

            # first move has to include middle
            has_middle = (7,7) in play_coords
            first_move = self.first_move()
            if not has_middle and first_move: raise Exception("First move must include middle space")

            # letters must be in the tray
            cur_letters = [x for x in tray]
            for l in play_letters:
                if len(l) > 2 or len(l) < 1: raise Exception("{l} is an invalid letter option")
                if len(l) == 2: l = l[0:1] # blank
                if not re.match(r"[A-Z?]", l): raise Exception("{l} is not a valid letter")
                if l not in cur_letters: raise Exception(f"{l} is not in the tray of {username}")
                cur_letters.remove(l)

            # must be in an empty space on the board
            board_tiles = self.taken_spaces()
            combined_coords = board_tiles + play_coords
            combos = list(itertools.combinations(combined_coords, 2))
            conflicts = [c for c in combos if c[0] == c[1]]
            if len(conflicts) > 0: raise Exception("Cannot put a letter where another already exists")

            # letters must all be in same column or row
            horizontal = all(x[0] == play_coords[0][0] for x in play_coords)
            vertical = all(x[1] == play_coords[0][1] for x in play_coords)
            if not (horizontal or vertical): raise Exception("All letters must be in same row or column")

            # must connect to existing letter
            if not first_move:
                found_connection = False
                sides = [(0,1),(0,-1),(1,0),(-1,0)]
                for c in play_coords:
                    for s in sides:
                        edge_coords = (c[0] + s[0], c[1] + s[1])
                        if (0 <= edge_coords[0] <= MAX_ROW) and (0 <= edge_coords[1] <= MAX_COLUMN):
                            if edge_coords in board_tiles:
                                found_connection = True
                if not found_connection: raise Exception("Word doesn't connect")


            # all letters must connect
            main_word = []
            extra_words = []
            if horizontal:
                row = play_coords[0][0]
                col_begin = min([x[1] for x in play_coords])
                max_column = max([x[1] for x in play_coords])
                for col in range(col_begin, max_column + 1):
                    coords = (row, col)
                    if coords not in combined_coords: raise Exception("There are spaces in the word")
                    main_word.append(self.tile_data(coords, play_tiles))
                    if coords in play_coords:
                        word = [self.tile_data(coords, play_tiles)]
                        word += self.get_up_tiles(coords, board_tiles, play_tiles)
                        word += self.get_down_tiles(coords, board_tiles, play_tiles)
                        if len(word) > 1: extra_words.append(word)
                main_word += self.get_left_tiles((row, col_begin), board_tiles, play_tiles)
                main_word += self.get_right_tiles((row, max_column), board_tiles, play_tiles)
            else:
                col = play_coords[0][1]
                row_begin = min([x[0] for x in play_coords])
                row_end = max([x[0] for x in play_coords])
                for row in range(row_begin, row_end + 1):
                    coords = (row, col)
                    if coords not in combined_coords: raise Exception("There are spaces in the word")
                    main_word.append(self.tile_data(coords, move.tiles()))
                    if coords in play_coords:
                        word = [self.tile_data(coords, play_tiles)]
                        word += self.get_left_tiles(coords, board_tiles, play_tiles)
                        word += self.get_right_tiles(coords, board_tiles, play_tiles)
                        if len(word) > 1: extra_words.append(word)
                main_word += self.get_up_tiles((row_begin, col), board_tiles, play_tiles)
                main_word += self.get_down_tiles((row_end, col), board_tiles, play_tiles)

            # must have at least one 2-letter word
            if len(main_word) < 2 and len(extra_words) == 0:
                raise Exception("Must have at least one word of at least two letters")

            # score the play
            score = self.score_word(main_word)
            for word in extra_words:
                score += self.score_word(word)
            if len(play_tiles) == 7: score += 50 # BINGO
            move.score = score

            # cleanup, remove used tiles and redraw
            self.update_tray(username, cur_letters)
            self.draw()

        elif move.type == 'pass':
            move.data = ''
        elif move.type == 'exchange':
            cur_letters = [x for x in tray]
            for l in move.data:
                if not re.match(r"[A-Z?]", l): raise Exception("{l} is not a valid letter")
                if l not in cur_letters: raise Exception(f"{l} is not in the tray of {username}")
                cur_letters.remove(l)

            # cleanup, remove used tiles and redraw
            self.update_tray(username, cur_letters)
            self.draw()
            self.bag += move.data
        #raise Exception("passed")
        return

    def update_tray(self, username, letters):
        if isinstance(letters, list): letters = "".join(cur_letters)
        if username == self.user_one:
            self.tray_one = letters
        elif username == self.user_two:
            self.tray_two = letters


    def get_up_tiles(self, coords, board_tiles, move_tiles):
        row, col, tiles = coords[0] - 1, coords[1], []
        while row >= 0 and (row, col) in board_tiles:
            tiles.append(self.tile_data((row, col), move_tiles))
            row -= 1
        return tiles

    def get_down_tiles(self, coords, board_tiles, move_tiles):
        row, col, tiles = coords[0] + 1, coords[1], []
        while row <= MAX_ROW and (row, col) in board_tiles:
            tiles.append(self.tile_data((row, col), move_tiles))
            row += 1
        return tiles

    def get_left_tiles(self, coords, board_tiles, move_tiles):
        row, col, tiles = coords[0], coords[1] - 1, []
        while col >= 0 and (row, col) in board_tiles:
            tiles.append(self.tile_data((row, col), move_tiles))
            col -= 1
        return tiles

    def get_right_tiles(self, coords, board_tiles, move_tiles):
        row, col, tiles = coords[0], coords[1] + 1, []
        while col <= MAX_COLUMN and (row, col) in board_tiles:
            tiles.append(self.tile_data((row, col), move_tiles))
            col += 1
        return tiles

    def score_word(self, word):
        score = sum(t["value"] for t in word)
        tws = sum([1 if 'tws' in t else 0 for t in word])
        dws = sum([1 if 'dws' in t else 0 for t in word])
        if dws > 0: score = score * 2 * dws
        if tws > 0: score = score * 3 * tws
        return score

    def taken_spaces(self):
        taken_spaces = [c for move in self.moves for c in move.coords().keys()]
        return taken_spaces

    def all_moves(self):
        all_moves = [move.tiles() for move in self.moves]
        return all_moves

    def whose_turn(self):
        m = self.moves
        l = len(m)
        if not l: return self.user_one
        elif l == 1: return self.user_two
        else: return m[-2].user

    def board(self):
        board = [['' for x in range(MAX_COLUMN + 1)] for y in range(MAX_ROW + 1)]
        for move in self.moves:
            if move.type == 'play':
                for match in move.tiles():
                    c = match[1]
                    board[c[0]][c[1]] = match[0]
        return board

    def pretty_board(self):
        l = ['────' for i in range(15)]
        c = ['┼' * 15]
        top_line = '┌' + '┬'.join(l) + '┐'
        blank_line = '├' + '┼'.join(l) + '┤'
        bottom_line = '└' + '┴'.join(l) + '┘'
        v = '│'
        rows = [f"{v}".join(l.center(4, ' ') for l in row) for row in self.board()]
        board = f"{top_line}\n{v}" + f"{v}\n{blank_line}\n{v}".join(rows) + f"{v}\n{bottom_line}"
        return board

    def tile_data(self, coords, play_tiles):
        board = self.board()
        data = {}
        modifier = None
        play_coords = [x[1] for x in play_tiles]
        if coords in play_coords:
            idx = play_coords.index(coords)
            data['letter'] = play_tiles[idx][0]
            data['value'] = LETTER_VALUES[data['letter'][0:1]]
            if coords in DLS_COORDS: data['value'] *= 2
            if coords in TLS_COORDS: data['value'] *= 3
            if coords in DWS_COORDS: data['dws'] = True
            if coords in TWS_COORDS: data['tws'] = True
        else:
            data['letter'] = board[coords[0]][coords[1]]
            data['value'] = LETTER_VALUES[data['letter'][0:1]]

        return data

    def trays(self):
        return {
            self.user_one: self.tray_one,
            self.user_two: self.tray_two
        }

    def tray(self, username):
        trays = self.trays()
        return trays[username] if username in trays else None

class GameCreate(GameBase):
    user_one: str
    user_two: str

