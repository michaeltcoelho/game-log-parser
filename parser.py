import enum
import re
from typing import List, Tuple


class Player:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def is_world_player(self):
        return self.name == '<world>'


class EventType(enum.Enum):
    INIT_GAME = 'InitGame'
    KILL = 'Kill'


class EventHandler:

    def __init__(self, repository: 'GameRepository' = None) -> None:
        self.repository: 'GameRepository' = repository

    def handle(self, event: str) -> None:
        raise NotImplementedError()


class InitGameEventHandler(EventHandler):

    def handle(self, event: str) -> None:
        print(f'InitGame: {event}')


class KillEventHandler(EventHandler):

    players_pattern = re.compile(
        r'[\d{,2}.+]: (?P<killer><?\w.+>?) killed (?P<killed>\w.+) by')

    def handle(self, event: str) -> None:
        player_killer, player_killed = self.get_players(event)

    def get_players(self, event) -> Tuple[Player, Player]:
        match = self.players_pattern.findall(event)
        killer, killed = match[0]
        return Player(killer), Player(killed)


class GameRepository:
    pass
