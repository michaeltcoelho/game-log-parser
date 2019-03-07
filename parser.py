import abc
import enum
import re
import uuid
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
    SHUTDOWN_GAME = 'ShutdownGame'
    KILL = 'Kill'


class EventHandler(abc.ABC):

    def __init__(self, repository: 'GameRepository' = None) -> None:
        self.repository = repository

    @abc.abstractmethod
    def handle(self, event: str) -> None:
        pass


class InitGameEventHandler(EventHandler):

    def handle(self, event: str) -> None:
        uid = str(uuid.uuid4())
        self.repository.add_new_game(uid)


class ShutdownGameEventHandler(EventHandler):

    def handle(self, event: str) -> None:
        if not self.repository.is_active_game_shutted_down():
            self.repository.shutdown_active_game()


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


class GameRepository(abc.ABC):

    @abc.abstractmethod
    def add_new_game(self, uid) -> None:
        pass

    @abc.abstractmethod
    def shutdown_active_game(self) -> None:
        pass

    @abc.abstractmethod
    def get_active_game(self) -> dict:
        pass

    @abc.abstractmethod
    def is_active_game_shutted_down(self) -> bool:
        pass


class MemoryGameRepository(GameRepository):

    store = {}
    active_game_uid = ''

    def add_new_game(self, uid) -> None:
        game = {
            'total_kills': 0,
            'players': [],
            'kills': {},
            'shutted_down': False
        }
        self.store[uid] = game
        self.active_game_uid = uid

    def shutdown_active_game(self) -> None:
        active_game = self.get_active_game()
        active_game['shutted_down'] = True

    def get_active_game(self):
        try:
            game = self.store[self.active_game_uid]
        except KeyError as err:
            # TODO: impl. informative exception
            raise Exception(str(err))
        else:
            return game

    def is_active_game_shutted_down(self) -> bool:
        active_game = self.get_active_game()
        return active_game['shutted_down']
