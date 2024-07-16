import pytest
from app import app
from flask import Flask

def test_echo():
    with app.test_client() as test_client:
        response = test_client.get('/')
        assert response.status_code == 200
        assert b"Game server is running" in response.data

def test_join_game():
    with app.test_client() as test_client:
        response = test_client.get("/new_game")
        assert response.status_code == 200

        game_id = response.json["id"]
        response = test_client.get(f"/join_game/{game_id}")
        assert response.status_code == 200

        # check that no one can join
        response = test_client.get(f"/join_game/{game_id}")
        assert response.status_code == 500        