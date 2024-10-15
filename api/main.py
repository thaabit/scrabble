import os
import mariadb
import sqlalchemy
import sys
import bcrypt


from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import create_engine, Session, select, or_
from typing import Annotated

from models.Game import Game, GameCreate
from models.User import User, UserCreate, UserUpdate
from models.Move import Move
from auth_handler import sign_jwt, oauth2_scheme, get_current_user, create_access_token

app = FastAPI()

mdb_url = "mariadb+pymysql://{}:{}@{}/{}?charset=utf8mb4".format(os.getenv("DB_USER"), os.getenv("DB_PASS"), os.getenv("DB_HOST"), os.getenv("DB_NAME"))
engine = create_engine(mdb_url)

@app.post("/login")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    with Session(engine) as session:
        query = select(User).where(User.username == form_data.username)
        try:
            user = session.exec(query).one()
            if user is None or not bcrypt.checkpw(bytes(form_data.password,'utf-8'), bytes(user.pwhash, 'utf-8')):
                raise HTTPException(status_code=400, detail="Incorrect username or password")
        except Exception as e:
            print(e.args)
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}


@app.get("/protected")
async def protected_route(username: str = Depends(get_current_user)):
    return {"message": f"Hello, {username}! This is a protected resource."}

@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}

@app.get("/")
async def hello():
    return {"success": 1}

@app.get("/health")
async def health():
    return {"success": 1}

@app.get("/game/{id}")
def read_game(id: int, username: str = Depends(get_current_user)):
    with Session(engine) as session:
        game = session.get(Game, id)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        return game

@app.post("/game")
def create_game(opponent: str, username: str = Depends(get_current_user)):
    with Session(engine) as session:
        game = Game.model_validate({
            'user_one': username,
            'user_two': opponent,
        })
        game.draw()
        session.add(game)
        session.commit()
        session.refresh(game)
        return game

@app.get("/games")
def list_games(auth_username: str = Depends(get_current_user)):
    with Session(engine) as session:
        try:
            statement = select(Game).where(or_(Game.user_one == auth_username, Game.user_two == auth_username))
            results = session.exec(statement)
            return results.all()
            #user = get_user(auth_username)
            #return user.games()
        except Exception as e:
            raise HTTPException(status_code=400, detail=e.args)

@app.get("/user/{id}")
def read_user(id: str):
    with Session(engine) as session:
        user = session.get(User, id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

@app.post("/user")
def create_user(user: UserCreate):
    pwhash = bcrypt.hashpw(bytes(user.password, 'utf-8'), bcrypt.gensalt(rounds=12))
    with Session(engine) as session:
        extra_data = {"pwhash": pwhash}
        db_user = User.model_validate(user, update=extra_data)
        try:
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return db_user
        except sqlalchemy.exc.IntegrityError as e:
            raise HTTPException(status_code=422, detail=e.args)

@app.get("/users")
def list_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return users

@app.post("/move")
def add_move(move: Move, auth_username: str = Depends(get_current_user)):
    move.user = auth_username
    with Session(engine) as session:
        game = session.get(Game, move.game_id)
        if not game: raise HTTPException(status_code=404, detail='Game not found')
        try:
            game.valid_move(move, auth_username)
        except Exception as e:
            raise HTTPException(status_code=422, detail=e.args)
        try:
            session.add(move)
            session.commit()
            session.refresh(move)
        except Exception as e:
            raise HTTPException(status_code=422, detail=e.args)
        return move

@app.get("/board/{game_id}")
def get_board(game_id: int):
    with Session(engine) as session:
        game = session.get(Game, game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")

        b = game.pretty_board()
        s1 = game.score(game.user_one)
        s2 = game.score(game.user_two)
        return f"{game.user_one}: {s1}\n{game.user_two}: {s2}\ntiles left: {len(game.bag)}\n{b}"

@app.get("/tray")
def get_tray(game_id: int, auth_username: str = Depends(get_current_user)):
    with Session(engine) as session:
        game = session.get(Game, game_id)
        if not game: raise HTTPException(status_code=404, detail='Game not found')
        return game.tray(auth_username)

def get_user(username):
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        results = session.exec(statement)
        return results.first()
