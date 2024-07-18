from collections import namedtuple
from dataclasses import asdict
from data.game_info import Ship, Board, GameState
import pytest
import json
from app import app

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

        board = Board([Ship(5, 0, 0, 0), Ship(3, 0, 2, 90)])
        print(asdict(board))
        json_board = json.dumps(asdict(board))
        res = test_client.get(f"/set_board/{game_id}?player_id={player1_id}&board={json_board}")
        assert res.status_code == 200
        res = test_client.get(f"/set_board/{game_id}?player_id={player2_id}&board={json_board}")        
        assert res.status_code == 200
        
        return GameIds(game_id, player1_id, player2_id)


def test_ship_kill(ids: GameIds):    
    with app.test_client() as test_client:
        res = test_client.get(f"/status/{ids.game_id}")
        assert res.json["state"] == GameState.TURN
