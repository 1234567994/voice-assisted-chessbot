import random

class AI:
    def __init__(self, color):
        self.color = color

    def get_move(self, board):
        # Get all possible moves for the AI's color
        all_moves = self.get_all_moves(board, self.color)
        
        if not all_moves:
            return None
        
        # Select a random move from all possible moves
        move = random.choice(all_moves)
        return move

    def get_all_moves(self, board, color):
        moves = []
        for row in range(8):
            for col in range(8):
                square = board.squares[row][col]
                if square.has_piece():
                    piece = square.piece
                    if piece.color == color:
                        # Calculate valid moves for the piece
                        piece_moves = board.calc_moves(piece, row, col, check_for_check=True)
                        moves.extend(piece_moves)
        return moves
