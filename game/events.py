import abc
import enum

from .games import GameRepository


class EventTypeNotMapped(ValueError):
    pass


class EventType(enum.Enum):
    INIT_GAME = 'InitGame'
    SHUTDOWN_GAME = 'ShutdownGame'
    KILL = 'Kill'


class EventHandler(abc.ABC):

    def __init__(self, repository: GameRepository = None) -> None:
        self.repository = repository

    @abc.abstractmethod
    def handle(self, event: str) -> None:
        pass


class EventObservable:

    def __init__(self) -> None:
        self.event_handlers = []

    def add_handler(self, event_type: str, event_handler: EventHandler) -> None:
        self.event_handlers.append((event_type, event_handler))

    def notify(self, event_type: str, event: str) -> None:
        for _type, event_handler in self.event_handlers:
            if _type == event_type:
                event_handler.handle(event)
