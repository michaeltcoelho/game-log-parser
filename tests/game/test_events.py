from game import GameRepository, EventType, EventHandler, EventObservable


class DummyRepository(GameRepository):

    def __init__(self):
        self.game_added = False
        self.active_game_shutted_down = False

    def get_games(self):
        pass

    def get_game_by_uid(self, uid):
        pass

    def get_active_game(self):
        pass

    def add(self, game):
        self.game_added = True

    def update(self, game):
        self.active_game_shutted_down = True


class TestEventObservable:

    def test_should_add_handler(self):

        class DummyInitGameHandler(EventHandler):
            def handle(self, event: str):
                pass

        event_stream = EventObservable()
        event_stream.add_handler(EventType.INIT_GAME, DummyInitGameHandler())

        registered_handlers = dict(event_stream.event_handlers)

        assert EventType.INIT_GAME in registered_handlers
        assert DummyInitGameHandler is registered_handlers[EventType.INIT_GAME].__class__

    def test_should_notify_handlers(self):

        class DummyInitGameEventHandler(EventHandler):

            def handle(self, event: str):
                self.repository.add(None)

        class DummyShutdownGameEventHandler(EventHandler):

            def handle(self, event: str):
                self.repository.update(None)

        repository = DummyRepository()

        event_stream = EventObservable()
        event_stream.add_handler(EventType.SHUTDOWN_GAME,
                                 DummyShutdownGameEventHandler(repository))
        event_stream.add_handler(EventType.INIT_GAME,
                                 DummyInitGameEventHandler(repository))
        event_stream.notify(EventType.INIT_GAME, 'InitGame: ')
        event_stream.notify(EventType.SHUTDOWN_GAME, 'ShutdownGame: ')

        assert repository.game_added is True
        assert repository.active_game_shutted_down is True
