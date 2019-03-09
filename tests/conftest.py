import pytest

from api import app as app_test

from game import Game, Player
from parser import MemoryGameRepository


@pytest.yield_fixture
def app():
    app_test.config['DEBUG'] = True
    app_test.config['TESTING'] = True
    app_test.config['SERVER_NAME'] = 'localhost'
    ctx = app_test.app_context()
    ctx.push()
    yield app_test
    ctx.pop()


@pytest.yield_fixture
def client(app):
    yield app.test_client()


@pytest.fixture
def game_with_player_with_one_kill():
    game = Game('foo')
    player = Player('bar')
    player.increase_kills(1)
    game.increase_total_kills()
    game.add_player(player)
    return game


@pytest.fixture
def game_repository():
    return MemoryGameRepository()
