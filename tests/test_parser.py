from unittest import mock

from parser import (EventType, EventHandler, InitGameEventHandler,
                    ShutdownGameEventHandler, KillEventHandler, EventObservable,
                    GameRepository, MemoryGameRepository, Player)


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
        assert len(active_game['players']) == 2
        assert 'Oootsimo' in active_game['players']
        assert 'Assasinu Credi' in active_game['players']
        assert active_game['kills']['Oootsimo'] == 1

        event = '1:23 Kill: 5 7 7: Oootsimo killed Fulera by MOD_ROCKET_SPLASH'
        handler.handle(event)

        assert active_game['total_kills'] == 2
        assert len(active_game['players']) == 3
        assert 'Fulera' in active_game['players']
        assert active_game['kills']['Oootsimo'] == 2

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_handle_kill_game_event_by_world_player(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add_new_game('abc')
        handler = KillEventHandler(memory_repo)
        event = '1:23 Kill: 5 7 7: Oootsimo killed Assasinu Credi by MOD_ROCKET_SPLASH'
        handler.handle(event)

        event = '1:23 Kill: 5 7 7: <world> killed Oootsimo by MOD_TRIGGER_HURT'
        handler.handle(event)

        active_game = memory_repo.get_active_game()
        assert active_game['total_kills'] == 2
        assert len(active_game['players']) == 2
        assert '<world>' not in active_game['players']
        assert active_game['kills']['Oootsimo'] == 0


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

            def add_new_game(self, uid):
                self.game_added = True

            def shutdown_active_game(self):
                self.active_game_shutted_down = True

            def get_active_game(self):
                pass

            def is_active_game_shutted_down(self):
                return self.active_game_shutted_down

            def add_player(self, player):
                pass

            def increase_kills_for_player(self, player, kills):
                pass

            def decrease_kills_for_player(self, player, kills):
                pass

            def increment_total_kills(self):
                pass

        class DummyInitGameEventHandler(EventHandler):

            def handle(self, event: str):
                self.repository.add_new_game('abc')

        class DummyShutdownGameEventHandler(EventHandler):

            def handle(self, event: str):
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


class TestMemoryGameRepository:

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

        assert not memory_repo.is_active_game_shutted_down()

        memory_repo.shutdown_active_game()

        assert memory_repo.is_active_game_shutted_down()

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_add_players(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add_new_game('abc')
        memory_repo.add_player(Player('Fulera'))
        active_game = memory_repo.get_active_game()
        assert len(active_game['players'])
        assert 'Fulera' in active_game['players']

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_not_add_same_player_twice(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add_new_game('abc')
        memory_repo.add_player(Player('Fulera'))
        memory_repo.add_player(Player('Fulera'))
        active_game = memory_repo.get_active_game()
        assert len(active_game['players']) == 1

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_increase_kills_for_player(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add_new_game('abc')
        player = Player('michaeltcoelho')
        memory_repo.add_player(player)
        memory_repo.increase_kills_for_player(player, 1)

        active_game = memory_repo.get_active_game()
        assert active_game['kills'][player.name] == 1

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_decrease_kills_for_player(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add_new_game('abc')
        player = Player('michaeltcoelho')
        memory_repo.add_player(player)
        memory_repo.increase_kills_for_player(player, 2)
        memory_repo.decrease_kills_for_player(player, 1)

        active_game = memory_repo.get_active_game()
        assert active_game['kills'][player.name] == 1

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_increment_total_kills(self):
        memory_repo = MemoryGameRepository()
        memory_repo.add_new_game('abc')
        active_game = memory_repo.get_active_game()

        memory_repo.increment_total_kills()
        assert active_game['total_kills'] == 1

        memory_repo.increment_total_kills()
        assert active_game['total_kills'] == 2
