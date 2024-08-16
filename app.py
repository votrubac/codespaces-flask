import flask
import json
from dataclasses import asdict, replace
from data.game_info import Player, GameInfo, Board, Turn, TurnResult, TurnRule, Ship
from uuid import uuid4
from flask import Flask
from flask import request
from flask_cors import CORS
from random import randint, shuffle
from flask_caching import Cache

test_game_id = "aaa-aaa-aaa"

config = {
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DEFAULT_TIMEOUT": 86400,  # in seconds, keep a game around for 24 hours max.
    "CACHE_THRESHOLD": 10000,  # increasing the default (500) to support more active games.
    "CACHE_DIR": "/tmp",
}
app = Flask(__name__)
CORS(app)

# tell Flask to use the above defined config
app.config.from_mapping(config)
game_cache = Cache(app)


def rand_xyz() -> str:
    a, z = ord("a"), ord("z")
    return "".join(chr(randint(a, z)) for _ in range(0, 3))


def test_uuid(ch: str) -> str:
    return f"{ch * 8}-{ch * 4}-{ch * 4}-{ch * 4}-{ch * 12}"


@app.route("/")
def hello_world():
    return f"Game server is running. Flask version {flask.__version__}."


@app.route("/new_game")
def new_game():
    id = test_game_id  # test id
    turn_rule = TurnRule(request.args.get("turn_rule"))
    while id and game_cache.has(id):
        id = f"{rand_xyz()}-{rand_xyz()}-{rand_xyz()}"
    game = GameInfo(id, turn_rule)
    player1_id = test_uuid("a") if game.id == test_game_id else str(uuid4())
    player1 = Player(player1_id, "Player 1")
    game.players[player1.id] = player1
    game.player_turns[player1.id] = []
    game_cache.set(id, game)
    return {"id": id, "player": player1}


@app.route("/join_game/<id>")
def join_game(id: str):
    if not game_cache.has(id):
        raise RuntimeError(f"Game {id} does not exists.")
    game: GameInfo = game_cache.get(id)
    if len(game.players) == game.max_players:
        raise RuntimeError(f"Game {id} is full.")
    player2_id = test_uuid("b") if game.id == test_game_id else str(uuid4())
    player2 = Player(player2_id, "Player 2")
    game.players[player2.id] = player2
    game.player_turns[player2.id] = []
    if len(game.players) == game.max_players:
        # starting the game (TODO: support min_players)
        game.player_order = list(game.players.keys())
        shuffle(game.player_order)
    game_cache.set(id, game)
    return {"id": id, "player": player2}


@app.route("/player_ready/<id>")
def player_ready(id: str):
    if not game_cache.has(id):
        raise RuntimeError(f"Game {id} does not exists.")
    game: GameInfo = game_cache.get(id)
    player_id = request.args.get("player_id")
    ready = True if request.args.get("ready").lower() == "true" else False

    if player_id not in game.players:
        raise RuntimeError(f"Incorrect player id: {player_id}.")

    if ready and player_id not in game.boards:
        player_name = game.players[player_id].name
        raise RuntimeError(f"Board for {player_name} has not been set.")

    if len(game.players) >= game.min_players and len(game.players) == len(
        game.ready_players
    ):
        # Cannot change once all players are ready.
        return {"ready": True}

    if ready:
        if player_id not in game.ready_players:
            game.ready_players.append(player_id)
    else:
        if player_id in game.ready_players:
            game.ready_players.remove(player_id)

    game_cache.set(id, game)
    return {"ready": ready}


@app.route("/set_board/<id>")
def set_board(id: str):
    if not game_cache.has(id):
        raise RuntimeError(f"Game {id} does not exists.")
    game: GameInfo = game_cache.get(id)
    player_id = request.args.get("player_id")
    if player_id not in game.players:
        raise RuntimeError(f"Incorrect player id: {player_id}.")
    if player_id in game.ready_players:
        player_name = game.players[player_id].name
        raise RuntimeError(f"Player {player_name} is ready to play.")
    ships_dict = json.loads(request.args.get("ships"))
    try:
        board = Board([Ship(set([(c[0], c[1]) for c in ship])) for ship in ships_dict])
        boardArray = [[(c[0], c[1]) for c in ship] for ship in ships_dict]

        game.boards[player_id] = board
        game_cache.set(id, game)
        return {"board": boardArray}

    except Exception as e:
        app.logger.error(e)
        raise


@app.route("/status/<id>")
def status(id: str):
    if not game_cache.has(id):
        raise RuntimeError(f"Game {id} does not exists.")
    return asdict(game_cache.get(id).get_status())


@app.route("/turn/<id>")
def turn(id: str):
    try:
        if not game_cache.has(id):
            raise RuntimeError(f"Game {id} does not exists.")
        game: GameInfo = game_cache.get(id)
        player_id = request.args.get("player_id")
        x = int(request.args.get("x"))
        y = int(request.args.get("y"))
        if player_id not in game.players:
            raise RuntimeError(f"Incorrect player id: {player_id}.")
        if len(game.players) != game.min_players:
            raise RuntimeError(f"Waiting for player(s) to join.")
        if len(game.players) != len(game.boards):
            raise RuntimeError(f"Waiting for player(s) to set the board.")

        cur_player_id = game.player_order[game.current_player]
        if player_id != cur_player_id:
            raise RuntimeError(
                f"Waiting for {game.players[cur_player_id].name}'s turn."
            )

        other_player_id = game.player_order[
            (game.current_player + 1) % len(game.player_order)
        ]
        ships = game.boards[other_player_id].ships
        cells = []
        turn_result = TurnResult.MISS
        for ship in ships:
            turn_result = ship.turn(x, y)
            if turn_result == TurnResult.KILL:
                cells = [[x, y] for x, y in ship.cells]
            if turn_result != TurnResult.MISS:
                break

        game_over = TurnResult.KILL and len(ships) == sum(
            1 for ship in ships if ship.killed()
        )

        if game_over:
            game.winner = game.players[cur_player_id].name
        elif game.turn_rule == TurnRule.ONE_BY_ONE or turn_result == TurnResult.MISS:
            # Switching the turn.
            game.current_player = (game.current_player + 1) % len(game.players)

        turn = Turn(x, y, turn_result, cells)
        game.player_turns[player_id].append(turn)
        game_cache.set(id, game)
        return asdict(turn)
    except Exception as e:
        app.logger.error(e)
        raise
