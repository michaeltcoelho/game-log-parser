from unittest import mock

import pytest

from parser import (EventType, EventHandler, InitGameEventHandler,
                    ShutdownGameEventHandler, KillEventHandler, EventObservable,
                    GameRepository, MemoryGameRepository, Game, Player,
                    GameDoesNotExist)


class TestEventHandler:

    def test_should_get_players_with_world_killer(self):
        game = Game('abc')
        handler = KillEventHandler()
        event = '1:26 Kill: 1022 4 22: <world> killed Zeh by MOD_TRIGGER_HURT'
        killer, killed = handler.get_players(game, event)
        assert killer.is_world() is True
        assert not killed.is_world()
        assert str(killed) == 'Zeh'

    def test_should_get_players(self):
        game = Game('abc')
        handler = KillEventHandler()
        event = '1:26 Kill: 1022 4 22: Foo killed Bar by MOD_TRIGGER_HURT'
        killer, killed = handler.get_players(game, event)
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
        memory_repo.add(Game('abc'))
        handler = ShutdownGameEventHandler(memory_repo)
        handler.handle('20:37 ShutdownGame:')
        game = memory_repo.get_active_game()
        assert game.is_shutted_down() is True

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_handle_kill_game_event(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add(Game('abc'))
        handler = KillEventHandler(memory_repo)
        event = '1:23 Kill: 5 7 7: Oootsimo killed Assasinu Credi by MOD_ROCKET_SPLASH'
        handler.handle(event)

        active_game = memory_repo.get_active_game()
        assert active_game.total_kills == 1
        assert len(active_game.players) == 2
        assert active_game.has_player('Oootsimo') is True
        assert active_game.has_player('Assasinu Credi') is True
        assert active_game.get_player('Oootsimo').kills == 1

        event = '1:23 Kill: 5 7 7: Oootsimo killed Fulera by MOD_ROCKET_SPLASH'
        handler.handle(event)

        assert active_game.total_kills == 2
        assert len(active_game.players) == 3
        assert active_game.has_player('Fulera') is True
        assert active_game.get_player('Oootsimo').kills == 2

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_handle_kill_game_event_by_world_player(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add(Game('abc'))
        handler = KillEventHandler(memory_repo)
        event = '1:23 Kill: 5 7 7: Oootsimo killed Assasinu Credi by MOD_ROCKET_SPLASH'
        handler.handle(event)

        event = '1:23 Kill: 5 7 7: <world> killed Oootsimo by MOD_TRIGGER_HURT'
        handler.handle(event)

        active_game = memory_repo.get_active_game()
        assert active_game.total_kills == 2
        assert len(active_game.players) == 2
        assert active_game.has_player('<world>') is False
        assert active_game.get_player('Oootsimo').kills == 0


class TestEventObservable:

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

        class DummyInitGameEventHandler(EventHandler):

            def handle(self, event: str):
                self.repository.add(None)

        class DummyShutdownGameEventHandler(EventHandler):

            def handle(self, event: str):
                self.repository.update(None)

        repository = TestEventObservable.DummyRepository()

        event_stream = EventObservable()
        event_stream.add_handler(EventType.SHUTDOWN_GAME,
                                 DummyShutdownGameEventHandler(repository))
        event_stream.add_handler(EventType.INIT_GAME,
                                 DummyInitGameEventHandler(repository))
        event_stream.notify(EventType.INIT_GAME, 'InitGame: ')
        event_stream.notify(EventType.SHUTDOWN_GAME, 'ShutdownGame: ')

        assert repository.game_added is True
        assert repository.active_game_shutted_down is True


class TestMemoryGameRepository:

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_add_new_game(self):
        game = Game('abc')
        memory_repo = MemoryGameRepository()
        memory_repo.add(game)
        assert memory_repo.get_active_game() is game
        assert memory_repo.active_game_uid == 'abc'

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_active_game_uid_be_the_last_added(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add(Game('xyz'))
        memory_repo.add(Game('abc'))
        assert memory_repo.active_game_uid == 'abc'

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_get_games(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add(Game('abc'))
        assert 'abc' in memory_repo.get_games()

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_get_games_by_id(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add(Game('abc'))
        assert memory_repo.get_game_by_uid('abc')

        with pytest.raises(GameDoesNotExist):
            memory_repo.get_game_by_uid('asdasdasd')
