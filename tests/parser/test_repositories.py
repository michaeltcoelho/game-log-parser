from unittest import mock

import pytest

from game.games import Game, GameDoesNotExist
from parser import MemoryGameRepository


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
