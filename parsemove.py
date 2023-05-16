import chess

def parse_move(move_str, board):
    # Check if the move is in UCI format (e.g., 'e2e4')
    try:
        move = chess.Move.from_uci(move_str)
        if move in board.legal_moves:
            return move
    except ValueError:
        pass

    # Check if the move is in long algebraic notation format (e.g., 'e2-e4')
    try:
        move = chess.Move.from_uci(chess.SQUARE_NAMES.index(move_str[:2].lower()) + chess.SQUARE_NAMES.index(move_str[2:].lower()) * 64)
        if move in board.legal_moves:
            return move
    except (ValueError, IndexError):
        pass

    # Check if the move is in short algebraic notation format (e.g., 'e4')
    for move in board.legal_moves:
        if move_str.lower() == board.san(move).lower():
            return move

    # Check if the move is in "piece to square" format (e.g., 'pawn to e4')
    try:
        move_parts = move_str.lower().split()
        if len(move_parts) == 3:
            piece_part = move_parts[0]
            square_part = move_parts[-1]
            if piece_part == "to":
                piece_part = move_parts[1]
            piece_type_map = {'pawn': chess.PAWN, 'knight': chess.KNIGHT, 'bishop': chess.BISHOP, 'rook': chess.ROOK, 'queen': chess.QUEEN, 'king': chess.KING}
            piece_type = None
            for key, value in piece_type_map.items():
                if key.startswith(piece_part) or key[0] == piece_part:
                    piece_type = value
                    break
            if piece_type is not None:
                for move in board.legal_moves:
                    if board.piece_type_at(move.from_square) == piece_type and chess.SQUARE_NAMES[move.to_square] == square_part:
                        return move
        elif len(move_parts) == 2:
            piece_part = move_parts[0]
            square_part = move_parts[1]
            piece_type_map = {'pawn': chess.PAWN, 'knight': chess.KNIGHT, 'bishop': chess.BISHOP, 'rook': chess.ROOK, 'queen': chess.QUEEN, 'king': chess.KING}
            piece_type = None
            for key, value in piece_type_map.items():
                if key.startswith(piece_part) or key[0] == piece_part:
                    piece_type = value
                    break
            if piece_type is not None:
                for move in board.legal_moves:
                    if board.piece_type_at(move.from_square) == piece_type and chess.SQUARE_NAMES[move.to_square] == square_part:
                        return move
    except (ValueError, IndexError):
        pass

    return None