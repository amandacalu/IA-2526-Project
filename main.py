from random import randint
from src.game.player import Player
from src.game.board import Board

def main():
    mode = int(input("Game mode selection\n0 - Human Vs Human\n1 - Human Vs AI\n 2 - AI Vs AI\nEnter choice: "))
    if mode not in (0, 1, 2):
        return
    if mode == 0:
        playerX = Player(True, True)
        playerO = Player(False, True)
    elif mode == 1:
        if randint(0, 1) == 0:
            playerX = Player(True, True)
            playerO = Player(False, False)
        else:
            playerX = Player(False, True)
            playerO = Player(True, False)
    else:
        playerX = Player(True, False)
        playerO = Player(False, False)
    board = Board()
    print(board)
    print("Notes:\nIf you want to pop out, enter coordinates in format:\n0, col\ncol being the number of the column you want to pop out of\nIf the board is full, you can tie by inputing 'tie'")
    while board.state == ' ':
        playerX.turn(board)
        if board.state != ' ':
            break
        playerO.turn(board)
    print(board.state)

main()