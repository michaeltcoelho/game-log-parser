import uuid
import re
from typing import Tuple

from game import Game, GameDoesNotExist, Player, EventHandler


class InitGameEventHandler(EventHandler):

    def handle(self, event: str) -> None:
        game = Game(str(uuid.uuid4()))
        self.repository.add(game)


class ShutdownGameEventHandler(EventHandler):

    def handle(self, event: str) -> None:
        try:
            active_game = self.repository.get_active_game()
        except GameDoesNotExist:
            handler_name = self.__class__.__name__
            print(f'{handler_name}: No active game found.'
                  '** SHUTDOWN_GAME event might have been triggered before '
                  'INIT_GAME event.')
        else:
            active_game.shutdown()
            self.repository.update(active_game)


class KillEventHandler(EventHandler):

    players_pattern = re.compile(
        r'[\d{,2}.+]: (?P<killer><?\w.+>?) killed (?P<killed>\w.+) by')

    def handle(self, event: str) -> None:
        active_game = self.repository.get_active_game()
        player_killer, player_killed = self.get_players(active_game, event)
        if player_killer.is_world():
            player_killed.decrease_kills(1)
        else:
            active_game.add_player(player_killer)
            player_killer.increase_kills(1)
        active_game.add_player(player_killed)
        active_game.increase_total_kills()
        self.repository.update(active_game)

    def get_players(self, active_game: Game, event: str) -> Tuple[Player, Player]:
        killer, killed = self._get_players_names(event)
        player_killer = active_game.get_player(killer) or Player(killer)
        player_killed = active_game.get_player(killed) or Player(killed)
        return player_killer, player_killed

    def _get_players_names(self, event: str) -> Tuple[str, str]:
        match = self.players_pattern.findall(event)
        killer_name, killed_name = match[0]
        return killer_name, killed_name
