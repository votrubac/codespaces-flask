from dataclasses import dataclass
from dataclasses import field

@dataclass
class Player:
    id: str
    name: str

@dataclass
class GameInfo:
    """Class for keeping track of the game status."""
    id: str
    players: list[Player] = field(default_factory=list)
    max_players: int = 2
    min_players: int = 2

