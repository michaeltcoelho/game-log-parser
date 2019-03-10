from unittest import mock

from flask import url_for

from parser import MemoryGameRepository


class TestHealthCheck:

    def test_should_ping_return_pong(self, client):
        response = client.get(url_for('ping'))
        assert response.status_code == 200
        assert response.get_data() == b'pong!'


class TestGameAPI:

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_get_games(self, client, game_with_player_with_one_kill):
        memory_repo = MemoryGameRepository()
        memory_repo.add(game_with_player_with_one_kill)
        game_uid = game_with_player_with_one_kill.uid
        response = client.get(url_for('get_games'))
        assert response.status_code == 200
        assert 'games' in response.json
        assert response.json['games'][0]['uid'] == game_uid
        assert response.json['games'][0]['total_kills'] == 1

    @mock.patch.object(MemoryGameRepository, 'store', {})
    def test_should_get_game_by_uid(self, client, game_with_player_with_one_kill):
        memory_repo = MemoryGameRepository()
        memory_repo.add(game_with_player_with_one_kill)
        game = memory_repo.get_active_game()
        response = client.get(url_for('get_game_by_uid', uid=game.uid))
        assert response.status_code == 200
        assert game.total_kills == response.json['total_kills']
        assert [p.name for p in game.players] == response.json['players']

    def test_should_return_not_found_when_get_games_by_uid(self, client):
        response = client.get(url_for('get_game_by_uid', uid='asdasd'))
        assert response.status_code == 404
        assert response.json['message'] == 'Game not found'
