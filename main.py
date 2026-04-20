from src.game.board import Board
from src.game.player import Player
from src.ai.mcts import MCTSNode
import copy
import math
import pandas as pd
import numpy as np
from random import choice
from random import randint
from random import random

def main():
    mode = int(input("Game mode selection\n0 - Human Vs Human\n1 - Human Vs MCTS\n2 - Human Vs DT\n3 - MCTS vs MCTS\n4 - MCTS vs DT\n5 - Dataset generation\nEnter choice: "))
    if mode in (0, 1, 2, 3, 4):
        if mode == 0:
            playerX = Player(True, "human")
            playerO = Player(False, "human")
        elif mode == 1:
            if randint(0, 1) == 0:
                playerX = Player(True, "human")
                playerO = Player(False, "MCTS")
            else:
                playerX = Player(True, "MCTS")
                playerO = Player(False, "human")
        elif mode == 2:
            if randint(0, 1) == 0:
                playerX = Player(True, "human")
                playerO = Player(False, "DT")
            else:
                playerX = Player(True, "DT")
                playerO = Player(False, "human")
        elif mode == 3:
            playerX = Player(True, "MCTS")
            playerO = Player(False, "MCTS")
        else:
            if randint(0, 1) == 0:
                playerX = Player(True, "MCTS")
                playerO = Player(False, "DT")
            else:
                playerX = Player(True, "DT")
                playerO = Player(False, "MCTS")
        board = Board()
        print(board)
        print("Notes:\nIf you want to pop out, enter coordinates in format:\n0, col\ncol being the number of the column you want to pop out of\nIf the board is full, you can tie by inputing 'tie'")
        while board.state == ' ':
            playerX.turn(board)
            print(board)
            if board.state != ' ':
                break
            playerO.turn(board)
            print(board)
        print(board.state)
    if mode == 5:
        playerX = Player(True, "MCTS")
        playerO = Player(False, "MCTS")

main()
