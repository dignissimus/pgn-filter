# pgn-filter

A small program to query for games inside PGN documents.

You can supply basic queries using command line arguments
and you can write more advanced queries using python scripts.

# Example queries
## Games starting with d4
```python
from chess import Move

def query(game):
    first_move = list(game.mainline_moves())
    if first_move[0] == Move.from_uci("d2d4"):
        return True
    return False
```
## Games with no castling moves
```python
from chess import Board

def query(game):
    board = Board()
    for move in game.mainline_moves():
    if board.is_castling(move):
        return False
    return True
```

# Installation instructions
```bash
pip install pgn-filter
```

# Program usage
```
usage: pgn-filter [-h] [-f FILE] [-i] [-q QUERY] [-m rating] [-M rating] [-a rating] [-F] [-S]

A small program to query for games inside PGN documents

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  The PGN file to search through
  -i, --stdin           Read from STDIN
  -q QUERY, --query QUERY
                        The Python file containing the query to use
  -m rating, --minimum-rating rating
                        The minimum rating of games to consider
  -M rating, --maximum-rating rating
                        The maximum rating of games to consider
  -a rating, --average-rating rating
                        The rating range to consider
  -F, --fast            Only consider bullet games
  -S, --slow            Only consider blitz games and slower

Every month I look through some ten thousand games ~ Vladimir Kramnik
```
