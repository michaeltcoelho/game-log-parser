import enum


class EventType(enum.Enum):
    INIT_GAME = 'InitGame'
    KILL = 'Kill'


class EventHandler:

    def __init__(self, parser: 'Parser'):
        self.parser: Parser = parser


class InitGameEventHandler(EventHandler):

    def handle(self, event: str) -> None:
        self.parser.handle(event)


class KillEventHandler(EventHandler):

    def handle(self, event: str) -> None:
        self.parser.handle(event)


class GameRepository:
    pass


class Parser:

    def __init__(self, game_repository: GameRepository):
        self.repository: GameRepository = game_repository
        self.event_handlers = []

    def add_event_handler(self, event_type: str,
                          event_handler: EventHandler) -> None:
        self.event_handlers.append((event_type, event_handler))

    def _read_file(self, log_file: str):
        with open(log_file, 'rb') as file:
            for line in file:
                yield line

    def parse(self, log_file: str) -> None:
        for event in self._read_file(log_file):
            for event_handler in self.event_handlers:
                event_handler.handle(event)

    def save(self):
        pass


if __name__ == "__main__":
    game_repository = GameRepository()
    parser = Parser(game_repository)
    parser.add_event_handler(EventType.INIT_GAME, InitGameEventHandler(parser))
    parser.add_event_handler(EventType.KILL, KillEventHandler(parser))
    parser.parse('./data/games.log')
