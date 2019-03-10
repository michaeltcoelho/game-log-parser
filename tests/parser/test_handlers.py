from unittest import mock

from game import Game
from parser import MemoryGameRepository
from parser.handlers import (InitGameEventHandler, ShutdownGameEventHandler,
                             KillEventHandler)


class TestEventHandler:

    def test_should_get_players_with_world_killer(self):
        game = Game('abc')
        handler = KillEventHandler(None)
        event = '1:26 Kill: 1022 4 22: <world> killed Zeh by MOD_TRIGGER_HURT'
        killer, killed = handler.get_players(game, event)
        assert killer.is_world() is True
        assert not killed.is_world()
        assert str(killed) == 'Zeh'

    def test_should_get_players(self):
        game = Game('abc')
        handler = KillEventHandler(None)
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
