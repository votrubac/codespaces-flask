from dataclasses import dataclass
from dataclasses import field
from enum import Enum


class TurnResult(str, Enum):
    MISS = "MISS"
    HIT = "HIT"
    KILL = "KILL"


class TurnRule(str, Enum):
    ONE_BY_ONE = "ONE_BY_ONE"
    TILL_MISS = "TILL_MISS"


class GameState(str, Enum):
    LOBBY = "LOBBY"
    SETUP = "SETUP"
    TURN = "TURN"
    FINISHED = "FINISHED"


@dataclass
class Player:
    id: str
    name: str

@dataclass
class Ship:
    cells: set[tuple[int, int]]
    hits: set[tuple[int, int]] = field(default_factory=set)

    def killed(self) -> bool:
        return len(self.hits) == len(self.cells)

    def turn(self, x, y) -> TurnResult:
        if (x, y) in self.cells:
            self.hits.add((x, y))
            return TurnResult.KILL if self.killed() else TurnResult.HIT

        return TurnResult.MISS


@dataclass
class Ships:
    ships: list[Ship] = field(default_factory=list)


@dataclass
class Board:
    ships: list[Ship] = field(default_factory=list)


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
    turns: dict[str, list[Turn]]
    winner: str


@dataclass
class GameInfo:
    """Class for keeping track of the game status."""

    id: str
    turn_rule: TurnRule
    players: dict[str, Player] = field(default_factory=dict)
    boards: dict[str, Board] = field(default_factory=dict)
    player_order: list[str] = field(default_factory=list)
    player_turns: dict[str, list[Turn]] = field(default_factory=dict)
    current_player: int = 0
    winner: str = ""
    max_players: int = 2
    min_players: int = 2

    def get_game_state(self) -> GameState:
        return (
            GameState.LOBBY
            if len(self.players) < self.min_players
            else (
                GameState.SETUP
                if len(self.players) != len(self.boards)
                else GameState.FINISHED if self.winner else GameState.TURN
            )
        )

    def get_status(self) -> GameStatus:
        joined_players = [
            self.players[player_id].name for player_id in self.players.keys()
        ]
        players_order = [
            self.players[player_id].name for player_id in self.player_order
        ]
        turns = {
            self.players[player_id].name: turns
            for player_id, turns in self.player_turns.items()
        }
        return GameStatus(
            self.get_game_state(),
            self.current_player,
            joined_players,
            players_order,
            turns,
            self.winner,
        )
