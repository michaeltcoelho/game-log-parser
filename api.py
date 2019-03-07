from flask import Flask, jsonify

from parser import MemoryGameRepository, LogParser

app = Flask('kills')

game_repository = MemoryGameRepository()


@app.route('/ping')
def ping():
    return 'pong!'


@app.route('/games')
def games():
    return jsonify(game_repository.store), 200


if __name__ == '__main__':
    parser = LogParser(game_repository)
    parser.parse('./data/games.log')
    app.run()
