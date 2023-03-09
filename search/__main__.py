import importlib.util
import sys
from argparse import ArgumentParser

from .search import TimeControl, find_games

ERROR_COLOUR = "\033[91m"
RESET_COLOUR = "\033[0m"

def main():
    parser = ArgumentParser(
        prog="pgn-filter",
        description="A small program to query for games inside PGN documents",
        epilog="""
        Every month I look through some ten thousand games
        ~ Vladimir Kramnik
        """,
    )

    parser.add_argument("-f", "--file", help="The PGN file to search through")
    parser.add_argument("-i", "--stdin", action="store_true", help="Read from STDIN")
    parser.add_argument(
        "-q", "--query", help="The Python file containing the query to use"
    )
    parser.add_argument(
        "-n",
        "--number-of-games",
        metavar="number",
        type=int,
        help="The maximum number of games to return",
    )
    parser.add_argument(
        "-m",
        "--minimum-rating",
        metavar="rating",
        type=int,
        help="The minimum rating of games to consider",
    )
    parser.add_argument(
        "-M",
        "--maximum-rating",
        metavar="rating",
        type=int,
        help="The maximum rating of games to consider",
    )
    parser.add_argument(
        "-a", "--average-rating", metavar="rating", type=int,help="The rating range to consider"
    )
    parser.add_argument(
        "-F", "--fast", action="store_true", help="Only consider bullet games"
    )
    parser.add_argument(
        "-S", "--slow", action="store_true", help="Only consider blitz games and slower"
    )

    arguments = parser.parse_args()

    error = False
    if not arguments.file and not arguments.stdin:
        print(ERROR_COLOUR + "Error: You must specify an input source")
        error = True

    if arguments.file and arguments.stdin:
        print(
            ERROR_COLOUR
            + "Error: Cannot read from a file and while reading from sdtandard input",
        )
        error = True

    if arguments.fast and arguments.slow:
        print(ERROR_COLOUR + "Error: --fast and --slow cannot be used together")
        error = True


    if error:
        print(RESET_COLOUR, end="")
        parser.print_help()
        exit()

    stream = None
    if arguments.file:
        stream = open(arguments.file)

    if arguments.stdin:
        stream = sys.stdin

    query = None
    if arguments.query:
        specification = importlib.util.spec_from_file_location("query", arguments.query)
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        query = module.query

    time_controls = list(TimeControl)
    if arguments.fast:
        time_controls = [TimeControl.ULTRA_BULLET, TimeControl.BULLET]

    if arguments.slow:
        time_controls = [
            TimeControl.BLITZ,
            TimeControl.RAPID,
            TimeControl.CORRESPONDENCE,
        ]

    minimum_rating = arguments.minimum_rating
    maximum_rating = arguments.maximum_rating
    average_rating = arguments.average_rating
    games = find_games(
        stream,
        query=query,
        time_controls=time_controls,
        minimum_rating_bound=minimum_rating,
        maximum_rating_bound=maximum_rating,
        average_rating_bound=average_rating,
        number_of_games=arguments.number_of_games
    )

    has_tqdm = False
    try:
        from tqdm import tqdm
        has_tqdm = True
    except ImportError:
        pass

    should_display_progress_bar = has_tqdm and arguments.number_of_games
    if should_display_progress_bar:
        progress_bar = tqdm(total=arguments.number_of_games)

    for game in games:
        if should_display_progress_bar:
            progress_bar.update(1)
        print(game, end="\n\n")

    stream.close()


if __name__ == "__main__":
    main()
