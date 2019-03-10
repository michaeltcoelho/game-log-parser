import re
from typing import Generator

from game import GameRepository, EventObservable, EventType, EventTypeNotMapped

from parser.handlers import (InitGameEventHandler, ShutdownGameEventHandler,
                             KillEventHandler)


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
            return EventType(event_type).name
        except ValueError:
            raise EventTypeNotMapped()

    def _read_log_file(self, log_file: str) -> Generator[str, None, None]:
        with open(log_file, 'r') as file:
            for line in file:
                yield str(line)
