from dataclasses import dataclass
from dataclasses import field
from enum import Enum

@dataclass
class Player:
    id: str
    name: str

@dataclass
class Ship:
    type: int
    x: int
    y: int
    angle: int

@dataclass
class Board:
    ships: list[Ship] = field(default_factory=list)

class TurnResult(str, Enum):
    MISS = "MISS"
    HIT = "HIT"
    KILL = "KILL"

class GameState(str, Enum):
    LOBBY = "LOBBY"
    SETUP = "SETUP"
    TURN = "TURN"
    END = "END"

@dataclass
class Turn:
    x: int
    y: int
    result: TurnResult

@dataclass
class GameStatus:
    state: GameState
    current_player: int
    joined_players: list[str]
    players_order: list[str]
    turns: dict[str,list[Turn]] = field(default_factory=list)


@dataclass
class GameInfo:
    """Class for keeping track of the game status."""
    id: str
    players: dict[str,Player] = field(default_factory=dict)
    boards: dict[str,Board] = field(default_factory=dict)
    player_order: list[str] = field(default_factory=list)
    player_turns: dict[str,list[Turn]] = field(default_factory=dict)
    current_player: int = 0
    max_players: int = 2
    min_players: int = 2

    def get_game_state(self) -> GameState:
        return (
            GameState.LOBBY if len(self.players) < self.min_players else 
            GameState.SETUP if len(self.players) != len(self.boards) else
            GameState.TURN
        )

    def get_status(self) -> GameStatus:
        joined_players = [self.players[player_id].name for player_id in self.players.keys()] 
        players_order = [self.players[player_id].name for player_id in self.player_order]
        turns = {self.players[player_id].name: turns for player_id, turns in self.player_turns.items()}
        return GameStatus(self.get_game_state(), self.current_player, joined_players, players_order, turns)


