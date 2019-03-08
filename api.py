from flask import Flask, jsonify

from parser import GameDoesNotExist, MemoryGameRepository, LogParser

app = Flask('game')

game_repository = MemoryGameRepository()


def format_game_to_dict(game):
    return {
        'total_kills': game.total_kills,
        'players': [player.name for player in game.players],
        'kills': {player.name: player.kills for player in game.players},
    }


@app.route('/ping')
def ping():
    return 'pong!'


@app.route('/games', methods=['GET'])
def get_games():
    games = game_repository.get_games()
    response = {}
    for uid, game in games.items():
        response[uid] = format_game_to_dict(game)
    return jsonify({'games': response}), 200


@app.route('/games/<uid>', methods=['GET'])
def get_games_by_id(uid):
    try:
        game = game_repository.get_game_by_uid(uid)
        return jsonify(format_game_to_dict(game)), 200
    except GameDoesNotExist:
        response = {
            'message': 'Game not found.'
        }
        return jsonify(response), 404


if __name__ == '__main__':
    parser = LogParser(game_repository)
    parser.parse('./data/games.log')

    app.run()
