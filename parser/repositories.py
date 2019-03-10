from typing import Dict

from game import Game, GameRepository, GameDoesNotExist


class MemoryGameRepository(GameRepository):

    store: Dict[str, Game] = {}
    active_game_uid: str = ''

    def get_games(self) -> dict:
        return self.store

    def get_game_by_uid(self, uid: str) -> Game:
        try:
            game = self.store[uid]
        except KeyError as err:
            raise GameDoesNotExist() from err
        else:
            return game

    def get_active_game(self) -> Game:
        try:
            game = self.store[self.active_game_uid]
        except KeyError as err:
            raise GameDoesNotExist() from err
        else:
            return game

    def add(self, game: Game) -> None:
        self.store[game.uid] = game
        self.active_game_uid = game.uid

    def update(self, game: Game) -> None:
        pass
