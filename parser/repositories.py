from game.games import Game, GameRepository, GameDoesNotExist


class MemoryGameRepository(GameRepository):

    store = {}
    active_game_uid = ''

    def get_games(self) -> dict:
        return self.store

    def get_game_by_uid(self, uid: str) -> Game:
        try:
            game = self.store[uid]
        except KeyError:
            raise GameDoesNotExist()
        else:
            return game

    def get_active_game(self) -> Game:
        try:
            game = self.store[self.active_game_uid]
        except KeyError:
            raise GameDoesNotExist()
        else:
            return game

    def add(self, game: Game) -> None:
        self.store[game.uid] = game
        self.active_game_uid = game.uid

    def update(self, game: Game) -> None:
        pass
