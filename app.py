import flask
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return f"Game server is running; Flask version {flask.__version__}."    

@app.route("/new_game")
def new_game():
    # Randomly generate game id and store it in cache.
    return "abx-xyi-zxs"

@app.route("/join_game/<game_id>")
def join_game(game_id: str):
    # Randomly generate game id and store it in cache.
    return f"joined {game_id}"

@app.route("/turn/<game_id>/<x>/<y>")
def turn(game_id: str, x: int, y: int):
    # Randomly generate game id and store it in cache.
    return { "x": x, "y": y, "result": "miss"}