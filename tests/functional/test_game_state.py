from app import app


def test_echo():
    with app.test_client() as test_client:
        response = test_client.get("/")
        assert response.status_code == 200
        assert b"Game server is running" in response.data


def test_new_game_inorrect_turn_type():
    with app.test_client() as test_client:
        response = test_client.get("/new_game?turn_rule=ABS")
        assert response.status_code == 500


def test_join_game():
    with app.test_client() as test_client:
        response = test_client.get("/new_game?turn_rule=TILL_MISS")
        assert response.status_code == 200

        game_id = response.json["id"]
        response = test_client.get(f"/join_game/{game_id}")
        assert response.status_code == 200

        # check that no one else can join
        response = test_client.get(f"/join_game/{game_id}")
        assert response.status_code == 500
