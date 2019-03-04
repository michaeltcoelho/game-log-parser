import re

from enum import Enum


class EventNotHandled(Exception):
    pass


class EventType(Enum):
    INIT_GAME = 'InitGame'
    SHUTDOWN = 'ShutdownGame'
    KILL = 'Kill'


class EventHandler:

    def handle(self, event: 'GameRepository') -> None:
        raise NotImplemented()


class InitEventHandler(EventHandler):

    def handle(self, event):
        pass


class KillEventHandler(EventHandler):

    PLAYER_NAMES_PATTERN = r'[\d{,2}.+]: (?P<killer><?\w.+>?) killed (?P<killed>\w.+) by'

    def handle(self, event):
        player_killer, player_killed = self.get_players(event)

    def get_players(self, event):
        killer, killed = self._get_players_names(event)
        return Player(killer), Player(killed)

    def _get_players_names(self, event):
        match = re.findall(self.PLAYER_NAMES_PATTERN, event)
        killer, killed = match[0]
        return killer, killed


class EventFactory:

    @staticmethod
    def get_handler(event_type):
        if event_type == EventType.INIT_GAME.value:
            return InitEventHandler()
        elif event_type == EventType.KILL.value:
            return KillEventHandler()
        else:
            raise EventNotHandled()


class Player:

    def __init__(self, name):
        self.name = name

    def is_world_player(self):
        return self.name == '<world>'


class GameRepository:

    def __init__(self):
        pass


class FileParser:

    EVENT_TYPE_PATTERN = r'^ (?P<time>\d{2}:\d{2}) (?P<event_type>\w+):'

    def __init__(self, log_file):
        self.log_file = log_file
        self.repository = GameRepository()

    def parse(self):
        for event in self._read_log_file(self.log_file):
            event_type = self._get_event_type(event)
            try:
                event_handler = EventFactory.get_handler(event_type)
                event_handler.handle(event)
            except EventNotHandled as err:
                pass

    def _read_log_file(self, log_file):
        with open(log_file, 'r') as file:
            for line in file:
                yield line

    def _get_event_type(self, event):
        matched = re.match(self.EVENT_TYPE_PATTERN, event)
        if matched:
            return matched.groupdict()['event_type']
        return None


if __name__ == "__main__":
    parser = FileParser('./data/games.log')
    parser.parse()
