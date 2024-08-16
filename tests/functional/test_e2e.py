from collections import namedtuple
from dataclasses import asdict
from data.game_info import Ship, GameState, TurnResult, TurnRule
import pytest
import json
from app import app

import logging

LOGGER = logging.getLogger(__name__)

GameIds = namedtuple("GameInfo", ["game_id", "player1_id", "player2_id"])


@pytest.fixture
def ids() -> GameIds:
    with app.test_client() as test_client:
        turn_rule = TurnRule.TILL_MISS
        res1 = test_client.get(f"/new_game?turn_rule={turn_rule}")
        assert res1.status_code == 200

        game_id = res1.json["id"]
        player1_id = res1.json["player"]["id"]

        res2 = test_client.get(f"/join_game/{game_id}")
        player2_id = res2.json["player"]["id"]
        test_ship3 = [(0, 2), (0, 3), (0, 4)]
        test_ship5 = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
        test_ship5_p2 = [(3, 0), (4, 0), (5, 0), (6, 0), (7, 0)]
        ships1 = [test_ship5, test_ship3]
        ships2 = [test_ship5_p2, test_ship3]

        res = test_client.get(
            f"/set_board/{game_id}?player_id={player1_id}&ships={json.dumps(ships1)}"
        )
        assert res.status_code == 200
        res = test_client.get(
            f"/set_board/{game_id}?player_id={player2_id}&ships={json.dumps(ships2)}"
        )
        assert res.status_code == 200
        res = test_client.get(
            f"/status/{game_id}"
        )
        assert res.status_code == 200
        assert res.json["turn_rule"] == turn_rule
        assert res.json["state"] == GameState.SETUP

        return GameIds(game_id, player1_id, player2_id)


def assert_ship_sinks(client, game_id, player_id, turns):
    for i, (x, y) in enumerate(turns):
        is_kill = i + 1 == len(turns)
        assert_turns(  # sinking the second ship.
            client,
            game_id,
            player_id,
            [
                (
                    x,
                    y,
                    TurnResult.KILL if is_kill else TurnResult.HIT,
                    turns if is_kill else [],
                )
            ],
        )


def assert_turns(
    client,
    game_id,
    player_id,
    expected: list[(int, int, TurnResult, list[tuple[int, int]])],
):
    for x, y, turn_result, cells in expected:
        res = client.get(f"/turn/{game_id}?player_id={player_id}&x={x}&y={y}")
        assert res.status_code == 200
        assert res.json["result"] == turn_result
        assert sorted(res.json["cells"]) == sorted(cells)

def test_turn_rules():
    with app.test_client() as test_client:
        game1 = test_client.get(f"/new_game?turn_rule={TurnRule.TILL_MISS}")
        game2 = test_client.get(f"/new_game?turn_rule={TurnRule.ONE_BY_ONE}")

        assert game1.status_code == 200
        assert game2.status_code == 200

        status1 = test_client.get(f"/status/{game1.json["id"]}")
        status2 = test_client.get(f"/status/{game2.json["id"]}")

        assert status1.status_code == 200
        assert status1.json["turn_rule"] == TurnRule.TILL_MISS
        assert status1.json["state"] == GameState.LOBBY
        assert status2.status_code == 200
        assert status2.json["turn_rule"] == TurnRule.ONE_BY_ONE
        assert status2.json["state"] == GameState.LOBBY


def test_update_board(ids: GameIds):
    with app.test_client() as test_client:
        res = test_client.get(
            f"/player_ready/{ids.game_id}?player_id={ids.player1_id}&ready=True"
        )
        assert res.status_code == 200

        ships = [[(0, 2), (0, 3), (0, 4)]]
        res = test_client.get(
            f"/set_board/{ids.game_id}?player_id={ids.player1_id}&ships={json.dumps(ships)}"
        )
        assert res.status_code == 500  # Cannot update board once ready.

        res = test_client.get(
            f"/player_ready/{ids.game_id}?player_id={ids.player1_id}&ready=False"
        )
        assert res.status_code == 200
        assert (
            res.json["ready"] == False
        )  # Can change the status when not all players are ready.

        res = test_client.get(
            f"/set_board/{ids.game_id}?player_id={ids.player1_id}&ships={json.dumps(ships)}"
        )
        assert res.status_code == 200  # Now the player can update the board.


def test_ready(ids: GameIds):
    with app.test_client() as test_client:
        res = test_client.get(
            f"/player_ready/{ids.game_id}?player_id={ids.player1_id}&ready=True"
        )
        assert res.status_code == 200

        res = test_client.get(
            f"/player_ready/{ids.game_id}?player_id={ids.player2_id}&ready=True"
        )
        assert res.status_code == 200

        res = test_client.get(
            f"/player_ready/{ids.game_id}?player_id={ids.player1_id}&ready=False"
        )
        assert res.status_code == 200
        assert (
            res.json["ready"] == True
        )  # Cannot change the ready status once all players are ready.


def test_win(ids: GameIds):
    with app.test_client() as test_client:
        res = test_client.get(
            f"/player_ready/{ids.game_id}?player_id={ids.player1_id}&ready=True"
        )
        assert res.status_code == 200

        res = test_client.get(
            f"/player_ready/{ids.game_id}?player_id={ids.player2_id}&ready=True"
        )
        assert res.status_code == 200

        res = test_client.get(f"/status/{ids.game_id}")
        assert res.json["state"] == GameState.TURN

        players = res.json["players_order"]
        current_player = res.json["current_player"]

        if players[current_player] != "Player 2":
            # Making a miss to switch turn to Player 1.
            assert_turns(
                test_client, ids.game_id, ids.player1_id, [(0, 0, TurnResult.MISS, [])]
            )

        player_id = ids.player2_id
        assert_ship_sinks(test_client, ids.game_id, player_id, [[0, 2], [0, 3], [0, 4]])
        assert_ship_sinks(
            test_client,
            ids.game_id,
            player_id,
            [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]],
        )

        res = test_client.get(f"/status/{ids.game_id}")
        assert res.json["state"] == GameState.FINISHED
        assert res.json["winner"] == "Player 2"
