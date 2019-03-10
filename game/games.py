import abc
from typing import Optional, MutableSet


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
        self.kills = max(self.kills - kills, 0)


class Game:

    def __init__(self, uid: str) -> None:
        self.uid = uid
        self.total_kills = 0
        self.shutted_down = False
        self.players: MutableSet[Player] = set([])

    def add_player(self, player: Player) -> None:
        self.players.add(player)

    def increase_total_kills(self) -> None:
        self.total_kills += 1

    def shutdown(self):
        self.shutted_down = True

    def is_shutted_down(self) -> bool:
        return self.shutted_down

    def get_player(self, name: str) -> Optional[Player]:
        player_found = None
        for player in self.players:
            if player.name == name:
                player_found = player
                break
        return player_found

    def has_player(self, name: str) -> bool:
        return bool(self.get_player(name))


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
