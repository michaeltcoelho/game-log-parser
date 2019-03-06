from parser import (EventType, EventHandler, InitGameEventHandler,
                    KillEventHandler, EventObservable)


class TestEventHandler:

    def test_should_get_players_with_world_killer(self):
        handler = KillEventHandler()
        event = '1:26 Kill: 1022 4 22: <world> killed Zeh by MOD_TRIGGER_HURT'
        killer, killed = handler.get_players(event)
        assert killer.is_world() is True
        assert not killed.is_world()
        assert str(killed) == 'Zeh'

    def test_should_get_players(self):
        handler = KillEventHandler()
        event = '1:26 Kill: 1022 4 22: Foo killed Bar by MOD_TRIGGER_HURT'
        killer, killed = handler.get_players(event)
        assert not killer.is_world()
        assert str(killer) == 'Foo'
        assert str(killed) == 'Bar'


class TestEventObservable:

    def test_should_add_handler(self):

        class DummyInitGameHandler:
            def handle(self, event: str):
                pass

        event_stream = EventObservable()
        event_stream.add_handler(EventType.INIT_GAME, DummyInitGameHandler())

        registered_handlers = dict(event_stream.event_handlers)

        assert EventType.INIT_GAME in registered_handlers
        assert DummyInitGameHandler is registered_handlers[EventType.INIT_GAME].__class__

    def test_should_notify_handlers(self):

        class DummyRepository:

            def __init__(self):
                self.initialized = False
                self.killed = False

            def initialize(self):
                self.initialized = True

            def has_initialized(self):
                return self.initialized

            def kill(self):
                self.killed = True

            def is_killed(self):
                return self.killed

        class DummyInitGameEventHandler(EventHandler):

            def handle(self, event: str) -> None:
                self.repository.initialize()

        class DummyKillEventHandler(EventHandler):

            def handle(self, event: str) -> None:
                self.repository.kill()

        repository = DummyRepository()

        event_stream = EventObservable()
        event_stream.add_handler(EventType.KILL, DummyKillEventHandler(repository))
        event_stream.add_handler(EventType.INIT_GAME,
                                 DummyInitGameEventHandler(repository))
        event_stream.notify(EventType.INIT_GAME, 'InitGame: ')
        event_stream.notify(EventType.KILL, 'Kill: ')

        assert repository.has_initialized()
        assert repository.is_killed()
