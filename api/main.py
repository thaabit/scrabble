import os
import mariadb
import sqlalchemy
import sys
import bcrypt

from fastapi import Depends, FastAPI, HTTPException, Query, APIRouter
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import create_engine, Session, select, or_, and_, SQLModel, text
from typing import Annotated

from models.Game import Game
from models.GameUser import GameUser
from models.User import User, UserCreate, UserUpdate
from models.Move import Move
from auth_handler import sign_jwt, oauth2_scheme, get_authed_username, create_access_token

app = FastAPI()
router = APIRouter()

origins = [
    "http://localhost:5173",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mdb_url = "mariadb+pymysql://{}:{}@{}/{}?charset=utf8mb4".format(os.getenv("DB_USER"), os.getenv("DB_PASS"), os.getenv("DB_HOST"), os.getenv("DB_NAME"))
engine = create_engine(mdb_url)

class LoginValidation(SQLModel):
    username: str
    password: str

def user_by_username(username):
    with Session(engine) as session:
        query = select(User).where(User.username == username)
        user = session.exec(query).one()
        return user

@router.get("/login_as/{username}")
def read_game(username: str, auth_username: str = Depends(get_authed_username)):
    if auth_username in (os.getenv("ADMIN") or '').split(","):
        access_token = create_access_token(data={"sub": username})
        return access_token
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.post("/login")
async def login_for_access_token(json: LoginValidation):
    with Session(engine) as session:
        query = select(User).where(User.username == json.username.strip())
        try:
            user = session.exec(query).one()
            if user is None or not bcrypt.checkpw(bytes(json.password,'utf-8'), bytes(user.pwhash, 'utf-8')):
                raise HTTPException(status_code=400, detail="Incorrect username or password")
        except Exception as e:
            print(e.args)
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}

@router.get("/protected")
async def protected_route(username: str = Depends(get_authed_username)):
    return {"message": f"Hello, {username}! This is a protected resource."}

@router.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}

@router.get("/")
async def hello():
    return {"success": 1}

@router.get("/health")
async def health():
    return {"success": 1}

@router.get("/game/{id}")
def read_game(id: int, auth_username: str = Depends(get_authed_username)):
    with Session(engine) as session:
        game = session.get(Game, id)
        tray = session.exec(select(GameUser).where(and_(GameUser.game_id == id, GameUser.username == auth_username))).first()
        if not game.game_over() and game.check_game_over():
            session.add(game)
            session.commit()

        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        return {
            "game":         game,
            "tray":         list(tray.tray),
            "played_tiles": game.hashed_moves(),
            "moves":        list(reversed(game.moves_with_tally(auth_username))),
            "scores":       game.scores(),
            "opponent":     game.opponent(auth_username),
            "whose_turn":   game.whose_turn(),
            "game_over":    game.game_over(),
            "unseen": {
                "tiles":      game.unseen_tiles(auth_username),
                "vowels":     game.unseen_vowels(auth_username),
                "consonants": game.unseen_consonants(auth_username),
                "bag":        game.bag_count(),
            },
        }

class GameValidation(SQLModel):
    opponent: str
@router.post("/game")
def create_game(args: GameValidation, username: str = Depends(get_authed_username)):
    with Session(engine) as session:
        game = Game()
        session.add(game)
        session.commit()
        session.refresh(game)
        user_one = GameUser.model_validate({ "username": username, "game_id": game.id })
        session.add(user_one)
        user_two = GameUser.model_validate({ "username": args.opponent, "game_id": game.id })
        session.add(user_two)
        game.draw()
        session.commit()
        session.refresh(game)
        return game

@router.get("/game")
def list_games(type: str = 'active', auth_username: str = Depends(get_authed_username)):
    with Session(engine) as session:
        try:
            auth_user = user_by_username(auth_username)
            session.add(auth_user)
            out = []
            sql = f'SELECT g.id, gu.tray, gu.ack_end FROM game_user gu JOIN game g ON g.id = gu.game_id WHERE gu.username = :un'
            if type == 'active':
                sql += " AND g.finished='0000-00-00 00:00:00'"
            elif type == 'inactive':
                sql += " AND g.finished!='0000-00-00 00:00:00'"
            elif type == 'unacknowledged':
                sql += " AND g.finished!='0000-00-00 00:00:00' AND gu.ack_end = 0 ORDER BY g.finished"
            games = session.execute(text(sql), params={"un": auth_username}).fetchall()
            for row in session.execute(text(sql), params={"un": auth_username}).fetchall():
                game = session.get(Game, row[0])
                out.append({
                    "id":            game.id,
                    "scores":        game.scores(),
                    "whose_turn":    game.whose_turn(),
                    "my_turn":       game.whose_turn() == auth_username,
                    "started":       game.created.date(),
                    "finished":      game.game_over(),
                    "finished_date": game.pretty_finished_date(),
                    "opponent":      game.opponent(auth_username),
                })
            out = sorted(out, key=lambda x: -1 if x['whose_turn'] == auth_username else 1 )
            return out

        except Exception as e:
            raise HTTPException(status_code=400, detail=e.args)

@router.get("/user/{id}")
def read_user(id: str, auth_username: str = Depends(get_authed_username)):
    with Session(engine) as session:
        user = session.get(User, id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

@router.post("/user")
def create_user(user: UserCreate):
    pwhash = bcrypt.hashpw(bytes(user.password, 'utf-8'), bcrypt.gensalt(rounds=12))
    with Session(engine) as session:
        extra_data = {"pwhash": pwhash}
        db_user = User.model_validate(user, update=extra_data)
        db_user.username = db_user.username.strip()
        try:
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            access_token = create_access_token(data={"sub": user.username})
            return_hash = {"username": db_user.username, "access_token": access_token, "token_type": "bearer"}
            return return_hash
        except sqlalchemy.exc.IntegrityError as e:
            print(e)
            raise HTTPException(status_code=422, detail="Username taken")

@router.get("/user")
def list_users(auth_username: str = Depends(get_authed_username)):
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return [user.username for user in users if user.username != auth_username]

@router.patch("/game/acknowledge/{game_id}")
def add_move(game_id: str, auth_username: str = Depends(get_authed_username)):
    with Session(engine) as session:
        game_user = session.exec(select(GameUser).where(and_(GameUser.game_id == int(game_id), GameUser.username == auth_username))).one()
        if not game_user: raise HTTPException(status_code=404, detail='Game not found')
        game_user.ack_end = 1
        session.add(game_user)
        session.commit()
        session.refresh(game_user)
        return { "success": 1 }


@router.post("/move")
def add_move(move: Move, auth_username: str = Depends(get_authed_username)):
    move.username = auth_username
    move.type = move.type if move.type else "play"
    with Session(engine) as session:
        game = session.get(Game, move.game_id)
        game_user = session.exec(select(GameUser).where(and_(GameUser.game_id == move.game_id, GameUser.username == auth_username)))
        if not game: raise HTTPException(status_code=404, detail='Game not found')
        try:
            game.valid_move(move, auth_username)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=422, detail=e.args)
        try:
            session.add(move)
            session.commit()
            session.refresh(move)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=422, detail=e.args)
        return move

@router.get("/board/{game_id}")
def get_board(game_id: int):
    with Session(engine) as session:
        game = session.get(Game, game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")

        b = game.pretty_board()
        scores = game.scores()
        return f"scores: {scores}\ntiles left: {len(game.bag)}\n{b}"

@router.get("/word")
def get_tray(words: list[str] = Query(default=...)):
    with Session(engine) as session:
        qs = ",".join("?"*len(words))
        sql = text(f'SELECT word FROM word WHERE word IN :word_list')
        valid = [x[0] for x in session.execute(sql, params={"word_list": words}).fetchall()]
        invalid = (list(set(words) - set(valid)))
        return { "invalid": invalid }

@router.get("/tray/{game_id}")
def get_tray(game_id: int, auth_username: str = Depends(get_authed_username)):
    with Session(engine) as session:
        game = session.get(Game, game_id)
        if not game: raise HTTPException(status_code=404, detail='Game not found')
        return {
            "tray": game.tray(auth_username),
            "game_over": game.game_over()
        }

def get_user(username):
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        results = session.exec(statement)
        return results.first()

app.include_router(router)
