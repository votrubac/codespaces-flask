import flask
from data.game_info import Player, GameInfo
from uuid import uuid4
from flask import Flask
from random import randint

app = Flask(__name__)


game_cache = {}

def rand_xyz() -> str:
    a, z = ord("a"), ord("z")
    return "".join(chr(randint(a, z)) for _ in range(0, 3))

@app.route("/")
def hello_world():
    return f"Game server is running;.. Flask version {flask.__version__}."    

@app.route("/new_game")
def new_game():
    while True:
        id = f"{rand_xyz()}-{rand_xyz()}-{rand_xyz()}"
        if id not in game_cache:
            game = GameInfo(id)
            player1 = Player(uuid4(), "Player 1")
            game.players.append(player1)
            game_cache[id] = game
            return {"id": id, "player": player1}

@app.route("/join_game/<id>")
def join_game(id: str):
    game: GameInfo = game_cache[id]
    if len(game.players) == game.max_players:
        raise RuntimeError(f"Game {id} is full.")
    player2 = Player(uuid4(), "Player 2")
    game.players.append(player2)
    return {"id": id, "player": player2}    