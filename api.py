from flask import Flask, jsonify

from flasgger import Swagger

from game.games import Game, GameDoesNotExist
from parser import LogParser, MemoryGameRepository


app = Flask('game')
app.config['SWAGGER'] = {
    'title': 'Game Documentation',
    'description': 'Luizalabs Challenge',
    'uiversion': 3,
    'specs_route': '/',
}
swagger = Swagger(app)

game_repository = MemoryGameRepository()


def format_game_to_dict(game: Game) -> dict:
    return {
        'uid': game.uid,
        'total_kills': game.total_kills,
        'players': [player.name for player in game.players],
        'kills': {player.name: player.kills for player in game.players},
    }


@app.route('/ping')
def ping():
    return 'pong!'


@app.route('/games', methods=['GET'])
def get_games():
    """Endpoint returning a list of Games.
    ---
    definitions:
      Game:
        type: object
        properties:
          kills:
            type: object
            properties:
              player_name:
                type: int
                description: Player's kills
          players:
            type: array
            items:
              type: string
              description: A list of players' names
          total_kills:
            type: int
            description: The total number of kills in the Game
          uid:
            type: string
            format: uuid
            description: Game's uid

    responses:
      200:
        description: A list of Games
        schema:
          $ref: '#/definitions/Game'
        examples:
          {
              "games": [
                  {
                    kills: {
                      Dono da Bola: 0,
                      Isgalamido: 1,
                      Mocinha: 0,
                      Zeh: 0
                    },
                    players: ["Zeh", "Mocinha", "Dono da Bola", "Isgalamido"],
                    total_kills: 4,
                    uid: "795bf0eb-5691-477d-ae91-856adb648385"
                  }
              ]
          }
    """
    games = game_repository.get_games()
    response = []
    for uid, game in games.items():
        response.append(format_game_to_dict(game))
    return jsonify({'games': response}), 200


@app.route('/games/<uid>', methods=['GET'])
def get_game_by_uid(uid):
    """Endpoint returning a Game by uid.
    ---
    parameters:
      - name: uid
        in: path
        type: string
        required: true

    definitions:
      Game:
        type: object
        properties:
          kills:
            type: object
            properties:
              player_name:
                type: int
                description: Player's kills
          players:
            type: array
            items:
              type: string
              description: A list of players' names
          total_kills:
            type: int
            description: The total number of kills in the Game
          uid:
            type: string
            format: uuid
            description: Game's uid

    responses:
      200:
        description: Game
        schema:
          $ref: '#/definitions/Game'
        examples:
          {
              kills: {
                  Dono da Bola: 0,
                  Isgalamido: 1,
                  Mocinha: 0,
                  Zeh: 0
              },
              players: ["Zeh", "Mocinha", "Dono da Bola", "Isgalamido"],
              total_kills: 4,
              uid: "795bf0eb-5691-477d-ae91-856adb648385"
          }
    """
    try:
        game = game_repository.get_game_by_uid(uid)
        return jsonify(format_game_to_dict(game)), 200
    except GameDoesNotExist:
        response = {
            'message': 'Game not found'
        }
        return jsonify(response), 404


if __name__ == '__main__':
    parser = LogParser(game_repository)
    parser.parse('./data/games.log')

    app.run()
