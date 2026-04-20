from src.game.board import Board

class Player:

    def __init__(self, isX: bool, isHuman: bool):
        self.isX = isX
        self.isHuman = isHuman

    def turn(self, board: Board):
        print(f"{self}'s turn")
        if self.isHuman:
            while True:
                toParse = input("Enter move coordinates: ").split(",")
                if (board.empty == 0 and len(toParse) == 0 and toParse[0] == "tie"):
                    board.state = "Game ends on a tie!"
                    break
                if len(toParse) != 2:
                    print("Invalid move! Try again.")
                    continue
                move = tuple((int(toParse[0]), int(toParse[1])))
                if move[0] not in range(0, 7) or move[1] not in range(1, 8):
                    print("Invalid move! Try again.")
                    continue
                if board.isLegal(self.isX, move): # type: ignore
                    board.playMove(str(self), move) # type: ignore
                    break
                else:
                    print("Invalid move! Try again.")
        else:
            print(NotImplemented)

    def __str__(self):
        if self.isX:
             return 'X'
        return 'O'