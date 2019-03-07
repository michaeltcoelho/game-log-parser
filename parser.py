import abc
import enum
import re
import uuid
from typing import Tuple, Generator


class GameDoesNotExist(Exception):
    pass


class Player:

    def __init__(self, name) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name

    def is_world(self) -> bool:
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
        if not player_killer.is_world():
            self.repository.add_player(player_killer)
            self.repository.increase_kills_for_player(player_killer, 1)
        else:
            self.repository.decrease_kills_for_player(player_killed, 1)
        self.repository.add_player(player_killed)
        self.repository.increment_total_kills()

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
    def get_games(self):
        pass

    @abc.abstractmethod
    def get_game_by_uid(self, uid: str) -> dict:
        pass

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

    @abc.abstractmethod
    def add_player(self, player: Player) -> None:
        pass

    @abc.abstractmethod
    def increase_kills_for_player(self, player: Player, kills: int) -> None:
        pass

    @abc.abstractmethod
    def decrease_kills_for_player(self, player: Player, kills: int) -> None:
        pass

    @abc.abstractmethod
    def increment_total_kills(self):
        pass


class MemoryGameRepository(GameRepository):

    store = {}
    active_game_uid = ''

    def get_games(self):
        return self.store

    def get_game_by_uid(self, uid: str) -> dict:
        try:
            game = self.store[uid]
        except KeyError:
            raise GameDoesNotExist()
        else:
            return game

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
        except KeyError:
            raise GameDoesNotExist()
        else:
            return game

    def is_active_game_shutted_down(self) -> bool:
        active_game = self.get_active_game()
        return active_game['shutted_down']

    def add_player(self, player: Player) -> None:
        active_game = self.get_active_game()
        players = active_game['players']
        if player.name not in players:
            players.append(player.name)

    def increase_kills_for_player(self, player: Player, kills: int) -> None:
        active_game = self.get_active_game()
        game_kills = active_game['kills']
        game_kills.setdefault(player.name, 0)
        game_kills[player.name] += kills

    def decrease_kills_for_player(self, player: Player, kills: int) -> None:
        active_game = self.get_active_game()
        game_kills = active_game['kills']
        game_kills.setdefault(player.name, 0)
        if game_kills[player.name] > 0:
            game_kills[player.name] -= kills

    def increment_total_kills(self) -> None:
        active_game = self.get_active_game()
        active_game['total_kills'] += 1


class LogParser:

    event_type_pattern = re.compile(r'(?P<time>\d{,2}:\d{2}) (?P<event_type>\w+):')
    shutdown_game_pattern = re.compile(r'(\s.*)?(?P<time>\d{,3}:\d{2}) [ -]+')

    def __init__(self, game_repository: GameRepository) -> None:
        self.game_repository = game_repository
        self.event_observable = EventObservable()
        self._register_events_handlers()

    def _register_events_handlers(self):
        self.event_observable.add_handler(EventType.INIT_GAME,
                                          InitGameEventHandler(self.game_repository))
        self.event_observable.add_handler(EventType.SHUTDOWN_GAME,
                                          ShutdownGameEventHandler(self.game_repository))
        self.event_observable.add_handler(EventType.KILL,
                                          KillEventHandler(self.game_repository))

    def parse(self, log_file: str) -> None:
        file = self._read_log_file(log_file)
        for event in file:
            event_type = self._get_event_type(event)
            if event_type is not None:
                self.event_observable.notify(event_type, event)

    def _get_event_type(self, event: str) -> str:
        has_shuttdown_pattern = self.shutdown_game_pattern.match(event)
        if has_shuttdown_pattern:
            return EventType.SHUTDOWN_GAME.value
        match = self.event_type_pattern.findall(event)
        event_time, event_type = match[0]
        try:
            return EventType(event_type)
        except ValueError:
            return None

    def _read_log_file(self, log_file: str) -> Generator[str, None, None]:
        with open(log_file, 'r') as file:
            for line in file:
                yield str(line)
