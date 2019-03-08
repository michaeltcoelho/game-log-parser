import abc
import enum
import re
import uuid
from typing import Generator, List, Optional, Tuple


class GameDoesNotExist(Exception):
    pass


class PlayerDoesNotExist(Exception):
    pass


class EventTypeNotMapped(ValueError):
    pass


class Player:

    def __init__(self, name) -> None:
        self.name = name
        self.kills = 0

    def __str__(self) -> str:
        return self.name

    def is_world(self) -> bool:
        return self.name == '<world>'

    def increase_kills(self, kills: int) -> None:
        self.kills += kills

    def decrease_kills(self, kills: int) -> None:
        if self.kills > 0:
            self.kills -= kills


class Game:

    def __init__(self, uid: str) -> None:
        self.uid = uid
        self.total_kills = 0
        self.shutted_down = False
        self.players: List[Player] = []

    def add_player(self, player: Player) -> None:
        if not self.has_player(player.name):
            self.players.append(player)

    def increase_total_kills(self) -> None:
        self.total_kills += 1

    def shutdown(self):
        self.shutted_down = True

    def is_shutted_down(self) -> bool:
        return self.shutted_down

    def has_player(self, name: str) -> bool:
        return any([True for player in self.players if player.name == name])

    def get_player(self, name: str) -> Optional[Player]:
        player = [player for player in self.players if player.name == name]
        return player[0] if player else None


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
        game = Game(str(uuid.uuid4()))
        self.repository.add(game)


class ShutdownGameEventHandler(EventHandler):

    def handle(self, event: str) -> None:
        active_game = self.repository.get_active_game()
        active_game.shutdown()
        self.repository.update(active_game)


class KillEventHandler(EventHandler):

    players_pattern = re.compile(
        r'[\d{,2}.+]: (?P<killer><?\w.+>?) killed (?P<killed>\w.+) by')

    def handle(self, event: str) -> None:
        active_game = self.repository.get_active_game()
        player_killer, player_killed = self.get_players(active_game, event)
        if player_killer.is_world():
            player_killed.decrease_kills(1)
        else:
            active_game.add_player(player_killer)
            player_killer.increase_kills(1)
        active_game.add_player(player_killed)
        active_game.increase_total_kills()
        self.repository.update(active_game)

    def get_players(self, active_game: Game, event: str) -> Tuple[Player, Player]:
        killer, killed = self._get_players_names(event)
        player_killer = active_game.get_player(killer) or Player(killer)
        player_killed = active_game.get_player(killed) or Player(killed)
        return player_killer, player_killed

    def _get_players_names(self, event: str) -> Tuple[str, str]:
        match = self.players_pattern.findall(event)
        killer_name, killed_name = match[0]
        return killer_name, killed_name


class EventObservable:

    def __init__(self) -> None:
        self.event_handlers = []

    def add_handler(self, event_type: str, event_handler: EventHandler) -> None:
        self.event_handlers.append((event_type, event_handler))

    def notify(self, event_type: str, event: str) -> None:
        for _type, event_handler in self.event_handlers:
            if _type == event_type:
                event_handler.handle(event)


class GameRepository(abc.ABC):

    @abc.abstractmethod
    def get_games(self) -> dict:
        pass

    @abc.abstractmethod
    def get_game_by_uid(self, uid: str) -> Game:
        pass

    @abc.abstractmethod
    def get_active_game(self) -> Game:
        pass

    @abc.abstractmethod
    def add(self, uid) -> None:
        pass

    @abc.abstractmethod
    def update(self, game: Game) -> None:
        pass


class MemoryGameRepository(GameRepository):

    store = {}
    active_game_uid = ''

    def get_games(self) -> dict:
        return self.store

    def get_game_by_uid(self, uid: str) -> Game:
        try:
            game = self.store[uid]
        except KeyError:
            raise GameDoesNotExist()
        else:
            return game

    def get_active_game(self) -> Game:
        try:
            game = self.store[self.active_game_uid]
        except KeyError:
            raise GameDoesNotExist()
        else:
            return game

    def add(self, game: Game) -> None:
        self.store[game.uid] = game
        self.active_game_uid = game.uid

    def update(self, game: Game) -> None:
        pass


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
            try:
                event_type = self._get_event_type(event)
            except EventTypeNotMapped:
                print(f'Event type {event} not mapped.')
            else:
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
            raise EventTypeNotMapped()

    def _read_log_file(self, log_file: str) -> Generator[str, None, None]:
        with open(log_file, 'r') as file:
            for line in file:
                yield str(line)
