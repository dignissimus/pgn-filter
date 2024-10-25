from enum import Enum

import chess
import chess.pgn
from multiprocessing import Pool
from dataclasses import dataclass
from typing import Callable, Optional


def read_games(stream):
    while True:
        game = chess.pgn.read_game(stream)
        if not game:
            return
        yield game


@dataclass
class GameFilter:
    query: Optional[Callable[chess.pgn.Game, bool]] = None
    time_controls: list[str] = None
    minimum_rating_bound: Optional[int] = None
    maximum_rating_bound: Optional[int] = None
    average_rating_bound: Optional[int] = None
    number_of_games: Optional[int] = None

    def __call__(self, game):
        query = self.query
        time_controls = self.time_controls
        minimum_rating_bound = self.minimum_rating_bound
        maximum_rating_bound = self.maximum_rating_bound
        average_rating_bound = self.average_rating_bound
        number_of_games = self.number_of_games

        should_check_elo = (
            minimum_rating_bound or maximum_rating_bound or average_rating_bound
        )
        if should_check_elo:
            white_elo_not_specified = "WhiteElo" not in game.headers
            black_elo_not_specified = "BlackElo" not in game.headers
            if white_elo_not_specified or black_elo_not_specified:
                return None

            white_elo = int(game.headers["WhiteElo"])
            black_elo = int(game.headers["BlackElo"])
            minimum_elo = min(white_elo, black_elo)
            maximum_elo = max(white_elo, black_elo)
            average_elo = (white_elo + black_elo) / 2

        if minimum_rating_bound and minimum_elo < minimum_rating_bound:
            return None

        if maximum_rating_bound and maximum_elo > maximum_rating_bound:
            return None

        if average_rating_bound:
            if minimum_elo < (average_rating_bound - 50):
                return None
            if maximum_elo > (average_rating_bound + 50):
                return None

        if time_controls:
            no_time_control_info = "TimeControl" not in game.headers
            if no_time_control_info:
                return None

            time_control_info = game.headers["TimeControl"]

            if not any(
                time_control.matches(time_control_info)
                for time_control in time_controls
            ):
                return None

        if query and not query(game):
            return None

        return game


def find_games(
    stream,
    /,
    query=None,
    time_controls=None,
    minimum_rating_bound=None,
    maximum_rating_bound=None,
    average_rating_bound=None,
    number_of_games=None,
):
    filter_game = GameFilter(
        query=query,
        time_controls=time_controls,
        minimum_rating_bound=minimum_rating_bound,
        maximum_rating_bound=maximum_rating_bound,
        average_rating_bound=average_rating_bound,
        number_of_games=number_of_games,
    )
    pool = Pool()
    count = 0
    for game in pool.imap_unordered(filter_game, read_games(stream)):
        if not game:
            continue
        count += 1
        yield game
        if count == number_of_games:
            return


class TimeControl(Enum):
    """
    Time controls are represented as bounds on the
    Estimated duration of a game in seconds
    """

    ULTRA_BULLET = (0, 29)
    BULLET = (30, 179)
    BLITZ = (180, 479)
    RAPID = (450, 1499)
    CLASSICAL = (1500, 21599)
    CORRESPONDENCE = (21600, 2147483647)

    def matches(self, other):
        if "+" not in other:
            return False
        clock, increment = other.split("+")
        lower_bound, upper_bound = self.value

        return lower_bound < int(clock) + 40 * int(increment) <= upper_bound
