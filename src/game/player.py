from src.game.board import Board

class Player:

    def __init__(self, isX: bool, type: str):
        self.isX = isX
        self.type = type

    def getPossibleMoves(self, board: Board):
        if (board.empty == 0):
            return ["tie"]
        moves = []
        for i in range(1, 8):
            if (board.board[5][i - 1] == 'X' and self.isX) or (board.board[5][i - 1] == 'O' and not self.isX):
                moves.append((0, i))
            for j in range(1, 7):
                if board.board[6 - j][i - 1] == ' ':
                    moves.append((j, i))
                    break
        return moves