from collections import namedtuple
from dataclasses import asdict
from data.game_info import Ship, Ships, Board, GameState, TurnResult
import pytest
import json
from app import app

import logging

LOGGER = logging.getLogger(__name__)

GameIds = namedtuple("GameInfo", ["game_id", "player1_id", "player2_id"])


@pytest.fixture
def ids() -> GameIds:
    with app.test_client() as test_client:
        res1 = test_client.get("/new_game?turn_rule=TILL_MISS")
        assert res1.status_code == 200

        game_id = res1.json["id"]
        player1_id = res1.json["player"]["id"]

        res2 = test_client.get(f"/join_game/{game_id}")
        player2_id = res2.json["player"]["id"]

        ships = Ships([Ship(5, 0, 0, 0), Ship(3, 0, 2, 90)])

        ships_dump = json.dumps(asdict(ships))
        res = test_client.get(
            f"/set_board/{game_id}?player_id={player1_id}&ships={ships_dump}"
        )
        assert res.status_code == 200
        res = test_client.get(
            f"/set_board/{game_id}?player_id={player2_id}&ships={ships_dump}"
        )
        assert res.status_code == 200

        return GameIds(game_id, player1_id, player2_id)


def make_turn(client, game_id, player_id, x, y):
    res = client.get(f"/turn/{game_id}?player_id={player_id}&x={x}&y={y}")
    assert res.status_code == 200

    return res.json["result"]


def test_ship_kill(ids: GameIds):
    with app.test_client() as test_client:
        res = test_client.get(f"/status/{ids.game_id}")
        assert res.json["state"] == GameState.TURN

        players = res.json["players_order"]
        current_player = res.json["current_player"]

        player_id = (
            ids.player1_id if players[current_player] == "Player 1" else ids.player2_id
        )

        assert make_turn(test_client, ids.game_id, player_id, 0, 0) == TurnResult.HIT
        assert make_turn(test_client, ids.game_id, player_id, 1, 0) == TurnResult.HIT
        assert make_turn(test_client, ids.game_id, player_id, 2, 0) == TurnResult.HIT        
        assert make_turn(test_client, ids.game_id, player_id, 3, 0) == TurnResult.HIT
        assert make_turn(test_client, ids.game_id, player_id, 4, 0) == TurnResult.KILL