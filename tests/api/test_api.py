from unittest import mock

from flask import url_for

import api
from parser import MemoryGameRepository


class TestHealthCheck:

    def test_should_ping_return_pong(self, client):
        response = client.get(url_for('ping'))
        assert response.status_code == 200
        assert response.get_data() == b'pong!'


class TestGameAPI:

    @mock.patch.object(MemoryGameRepository, 'store', {})
    @mock.patch.object(api, 'get_game_repository')
    def test_should_get_games(self, mocked_get_game_repository, client, game_repository,
                              game_with_player_with_one_kill):
        mocked_get_game_repository.return_value = game_repository
        game_repository.add(game_with_player_with_one_kill)
        game_uid = game_with_player_with_one_kill.uid
        response = client.get(url_for('get_games'))
        assert response.status_code == 200
        assert 'games' in response.json
        assert response.json['games'][game_uid]['total_kills'] == 1

    @mock.patch.object(MemoryGameRepository, 'store', {})
    @mock.patch.object(api, 'get_game_repository')
    def test_should_get_game_by_uid(self, mocked_get_game_repository, client,
                                    game_repository, game_with_player_with_one_kill):
        mocked_get_game_repository.return_value = game_repository
        game_repository.add(game_with_player_with_one_kill)
        game = game_repository.get_active_game()
        response = client.get(url_for('get_game_by_uid', uid=game.uid))
        assert response.status_code == 200
        assert game.total_kills == response.json['total_kills']
        assert [p.name for p in game.players] == response.json['players']

    def test_should_return_not_found_when_get_games_by_uid(self, client):
        response = client.get(url_for('get_game_by_uid', uid='asdasd'))
        assert response.status_code == 404
        assert response.json['message'] == 'Game not found'
