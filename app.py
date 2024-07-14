import flask
from flask import Flask
from random import randint

app = Flask(__name__)


game_cache = {}

def rand_xyz() -> str:
    a, z = ord("a"), ord("z")
    return "".join(chr(randint(a, z)) for _ in range(0, 3))

@app.route("/")
def hello_world():
    return f"Game server is running; Flask version {flask.__version__}."    

@app.route("/new_game")
def new_game():
    while True:
        id = f"{rand_xyz()}-{rand_xyz()}-{rand_xyz()}"
        if id not in game_cache:
            return id

@app.route("/join_game/<game_id>")
def join_game(game_id: str):
    # Randomly generate game id and store it in cache.
    return f"joined {game_id}"

@app.route("/turn/<game_id>/<x>/<y>")
def turn(game_id: str, x: int, y: int):
    # Randomly generate game id and store it in cache.
    return { "x": x, "y": y, "result": "miss"}