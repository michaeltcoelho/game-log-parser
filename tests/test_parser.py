from parser import InitGameEventHandler, KillEventHandler


class TestEventHandler:

    def test_should_handle_init_game_event(self):
        handler = InitGameEventHandler()
        event = '0:00 InitGame: \\sv_floodProtect\1\\sv_maxPing\0\\sv_minPing'
        handler.handle(event)

    def test_should_handle_kill_game_event_from_world(self):
        handler = KillEventHandler()
        event = '1:26 Kill: 1022 4 22: <world> killed Zeh by MOD_TRIGGER_HURT'
        killer, killed = handler.get_players(event)
        assert killer.is_world_player() == True
        assert not killed.is_world_player()
        assert str(killed) == 'Zeh'
