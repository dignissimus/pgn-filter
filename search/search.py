from enum import Enum

import chess
import chess.pgn


def find_games(
    stream,
    /,
    query=None,
    time_controls=None,
    minimum_rating_bound=None,
    maximum_rating_bound=None,
    average_rating_bound=None,
):
    while True:
        game = chess.pgn.read_game(stream)
        if not game:
            break

        should_check_elo = (
            minimum_rating_bound or maximum_rating_bound or average_rating_bound
        )
        if should_check_elo:
            white_elo_not_specified = "WhiteElo" not in game.headers
            black_elo_not_specified = "BlackElo" not in game.headers
            if white_elo_not_specified or black_elo_not_specified:
                continue

            white_elo = int(game.headers["WhiteElo"])
            black_elo = int(game.headers["BlackElo"])
            minimum_elo = min(white_elo, black_elo)
            maximum_elo = max(white_elo, black_elo)
            average_elo = (white_elo + black_elo) / 2

        if minimum_rating_bound and minimum_elo < minimum_rating_bound:
            continue
        if maximum_rating_bound and maximum_elo > maximum_rating_bound:
            continue
        if average_rating_bound:
            if minimum_elo < (average_elo - 50):
                continue
            if maximum_elo > (average_elo + 50):
                continue

        if query and not query(game):
            continue

        yield game


class TimeControl(Enum):
    """
    Time controls are represented as bounds on the
    Estimated duration of a game in seconds
    """

    ULTRA_BULLET = (0, 29)
    BULLET = (30, 179)
    BLITZ = (180, 479)
    CLASSICAL = (1500, 21599)
    CORRESPONDENCE = (21600, 2147483647)
