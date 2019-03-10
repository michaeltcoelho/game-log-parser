import abc
from typing import List, Optional


class GameDoesNotExist(Exception):
    pass


class PlayerDoesNotExist(Exception):
    pass


class Player:

    def __init__(self, name: str) -> None:
        self.name = name
        self.kills = 0

    def __str__(self) -> str:
        return self.name

    def is_world(self) -> bool:
        return self.name == '<world>'

    def increase_kills(self, kills: int) -> None:
        self.kills += kills

    def decrease_kills(self, kills: int) -> None:
        if self.kills > 0:
            self.kills -= kills


class Game:

    def __init__(self, uid: str) -> None:
        self.uid = uid
        self.total_kills = 0
        self.shutted_down = False
        self.players: List[Player] = []

    def add_player(self, player: Player) -> None:
        if not self.has_player(player.name):
            self.players.append(player)

    def increase_total_kills(self) -> None:
        self.total_kills += 1

    def shutdown(self):
        self.shutted_down = True

    def is_shutted_down(self) -> bool:
        return self.shutted_down

    def has_player(self, name: str) -> bool:
        return any([True for player in self.players if player.name == name])

    def get_player(self, name: str) -> Optional[Player]:
        player = [player for player in self.players if player.name == name]
        return player[0] if player else None


class GameRepository(abc.ABC):

    @abc.abstractmethod
    def get_games(self) -> dict:
        pass

    @abc.abstractmethod
    def get_game_by_uid(self, uid: str) -> Game:
        pass

    @abc.abstractmethod
    def get_active_game(self) -> Game:
        pass

    @abc.abstractmethod
    def add(self, game: Game) -> None:
        pass

    @abc.abstractmethod
    def update(self, game: Game) -> None:
        pass
