from game import Game, Player


class TestGame:

    def test_should_add_player(self):
        game = Game('abc')
        player = Player('foo')
        game.add_player(player)
        assert game.has_player(player.name)

    def test_should_not_add_same_player_twice(self):
        game = Game('abc')
        player = Player('foo')
        game.add_player(player)
        game.add_player(player)
        assert len(game.players) == 1

    def test_should_get_player(self):
        game = Game('abc')
        player = Player('foo')
        game.add_player(player)
        assert player is game.get_player(player.name)
        assert game.get_player('bar') is None

    def test_should_increase_game_total_kills_one_by_one(self):
        game = Game('abc')
        assert game.total_kills == 0
        game.increase_total_kills()
        assert game.total_kills == 1
        game.increase_total_kills() == 2

    def test_should_shutdown_game(self):
        game = Game('abc')
        assert game.is_shutted_down() is False
        game.shutdown()
        assert game.is_shutted_down() is True


class TestPlayer:

    def test_should_player_be_world(self):
        player = Player('<world>')
        assert player.is_world() is True

    def test_should_increase_player_kills(self):
        player = Player('foo')
        assert player.kills == 0
        player.increase_kills(1)
        assert player.kills == 1
        player.increase_kills(2)
        assert player.kills == 3

    def test_should_decrease_player_kills(self):
        player = Player('foo')
        player.increase_kills(2)
        assert player.kills == 2
        player.decrease_kills(1)
        assert player.kills == 1
