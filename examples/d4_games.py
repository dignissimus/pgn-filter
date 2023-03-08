from chess import Move


def query(game):
    first_move = list(game.mainline_moves())
    if first_move[0] == Move.from_uci("d2d4"):
        return True
    return False
