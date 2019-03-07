from unittest import mock

from parser import (EventType, EventHandler, InitGameEventHandler,
                    ShutdownGameEventHandler, KillEventHandler, EventObservable,
                    GameRepository, MemoryGameRepository)


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

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_handle_init_game_event(self):
        memory_repo = MemoryGameRepository()
        handler = InitGameEventHandler(memory_repo)
        handler.handle('  0:00 InitGame: \\sv_floodProtect\\1\\sv_maxPing\0')
        assert len(memory_repo.store) == 1

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_handle_shutdown_game_event(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add_new_game('abc')
        handler = ShutdownGameEventHandler(memory_repo)
        handler.handle('20:37 ShutdownGame:')
        shutted_down_game = memory_repo.get_active_game()
        assert shutted_down_game['shutted_down'] is True

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_handle_kill_game_evet(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add_new_game('abc')
        handler = KillEventHandler(memory_repo)
        event = '1:23 Kill: 5 7 7: Oootsimo killed Assasinu Credi by MOD_ROCKET_SPLASH'
        handler.handle(event)

        active_game = memory_repo.get_active_game()
        assert active_game['total_kills'] == 1
        assert 'Oootsimo' in active_game['players']
        assert 'Assasinu' in active_game['players']
        assert active_game['kills']['Ootsimo'] == 1


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
                self.active_game_shutted_down = False

            def add_new_game(self, uid) -> None:
                self.game_added = True

            def shutdown_active_game(self) -> None:
                self.active_game_shutted_down = True

            def get_active_game(self) -> dict:
                pass

            def is_active_game_shutted_down(self) -> bool:
                return self.active_game_shutted_down

        class DummyInitGameEventHandler(EventHandler):

            def handle(self, event: str) -> None:
                self.repository.add_new_game('abc')

        class DummyShutdownGameEventHandler(EventHandler):

            def handle(self, event: str) -> None:
                self.repository.shutdown_active_game()

        repository = DummyRepository()

        event_stream = EventObservable()
        event_stream.add_handler(EventType.SHUTDOWN_GAME,
                                 DummyShutdownGameEventHandler(repository))
        event_stream.add_handler(EventType.INIT_GAME,
                                 DummyInitGameEventHandler(repository))
        event_stream.notify(EventType.INIT_GAME, 'InitGame: ')
        event_stream.notify(EventType.SHUTDOWN_GAME, 'ShutdownGame: ')

        assert repository.game_added is True
        assert repository.is_active_game_shutted_down() is True


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
        assert active_game['shutted_down'] is False

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_active_game_uid_be_the_last_added(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add_new_game('xyz')
        memory_repo.add_new_game('abc')
        assert memory_repo.active_game_uid == 'abc'

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_shutdown_active_game(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add_new_game('abc')

        active_game = memory_repo.get_active_game()

        assert active_game['shutted_down'] is False

        memory_repo.shutdown_active_game()

        shutted_down_game = memory_repo.get_active_game()
        assert shutted_down_game['shutted_down'] is True
