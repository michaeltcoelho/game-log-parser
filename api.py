from flask import Flask, jsonify

from parser import GameDoesNotExist, MemoryGameRepository, LogParser

app = Flask('game')

game_repository = MemoryGameRepository()


@app.route('/ping')
def ping():
    return 'pong!'


@app.route('/games', methods=['GET'])
def get_games():
    response = {
        'games': game_repository.get_games(),
    }
    return jsonify(response), 200


@app.route('/games/<uid>', methods=['GET'])
def get_games_by_id(uid):
    try:
        game = game_repository.get_game_by_uid(uid)
        return jsonify(game), 200
    except GameDoesNotExist:
        response = {
            'message': 'Game not found.'
        }
        return jsonify(response), 404


if __name__ == '__main__':
    parser = LogParser(game_repository)
    parser.parse('./data/games.log')

    app.run()
