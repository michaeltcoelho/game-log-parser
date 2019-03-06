import enum
import re
from typing import Tuple


class Player:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def is_world(self):
        return self.name == '<world>'


class EventType(enum.Enum):
    INIT_GAME = 'InitGame'
    KILL = 'Kill'


class EventHandler:

    def __init__(self, repository: 'GameRepository' = None) -> None:
        self.repository = repository

    def handle(self, event: str) -> None:
        raise NotImplementedError()


class InitGameEventHandler(EventHandler):

    def handle(self, event: str) -> None:
        print(f'InitGame: {event}')


class ShutDownGameEventHandler(EventHandler):

    def handle(self, event: str) -> None:
        print(f'ShutDown: {event}')


class KillEventHandler(EventHandler):

    players_pattern = re.compile(
        r'[\d{,2}.+]: (?P<killer><?\w.+>?) killed (?P<killed>\w.+) by')

    def handle(self, event: str) -> None:
        player_killer, player_killed = self.get_players(event)

    def get_players(self, event) -> Tuple[Player, Player]:
        match = self.players_pattern.findall(event)
        killer, killed = match[0]
        return Player(killer), Player(killed)


class EventObservable:

    def __init__(self) -> None:
        self.event_handlers = []

    def add_handler(self, event_type: str, event_handler: EventHandler) -> None:
        self.event_handlers.append((event_type, event_handler))

    def notify(self, event_type: str, event: str):
        for _type, event_handler in self.event_handlers:
            if _type == event_type:
                event_handler.handle(event)


class GameRepository:
    pass
