from unittest import mock

from parser import (EventType, EventHandler, InitGameEventHandler,
                    KillEventHandler, EventObservable, GameRepository,
                    MemoryGameRepository)


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

        class DummyRepository(GameRepository):

            def __init__(self):
                self.game_added = False
                self.active_game_exited = False

            def add_new_game(self, uid) -> None:
                self.game_added = True

            def exit_active_game(self) -> None:
                self.active_game_exited = True

            def get_active_game(self) -> dict:
                pass

        class DummyInitGameEventHandler(EventHandler):

            def handle(self, event: str) -> None:
                self.repository.add_new_game('abc')

        class DummyExitGameEventHandler(EventHandler):

            def handle(self, event: str) -> None:
                self.repository.exit_active_game()

        repository = DummyRepository()

        event_stream = EventObservable()
        event_stream.add_handler(EventType.KILL, DummyExitGameEventHandler(repository))
        event_stream.add_handler(EventType.INIT_GAME,
                                 DummyInitGameEventHandler(repository))
        event_stream.notify(EventType.INIT_GAME, 'InitGame: ')
        event_stream.notify(EventType.KILL, 'Kill: ')

        assert repository.game_added is True
        assert repository.active_game_exited is True


class TestGameRepository:

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_add_new_game(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add_new_game('abc')

        assert memory_repo.active_game_uid == 'abc'

        active_game = memory_repo.get_active_game()
        assert active_game['total_kills'] == 0
        assert active_game['players'] == []
        assert active_game['kills'] == {}
        assert active_game['exited'] is False

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_active_game_uid_be_the_last_added(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add_new_game('xyz')
        memory_repo.add_new_game('abc')
        assert memory_repo.active_game_uid == 'abc'

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_exit_active_game(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add_new_game('abc')

        active_game = memory_repo.get_active_game()

        assert active_game['exited'] is False

        memory_repo.exit_active_game()

        exited_game = memory_repo.get_active_game()
        assert exited_game['exited'] is True
