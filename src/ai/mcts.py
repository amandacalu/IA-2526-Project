import copy
import math
import pandas as pd
import numpy as np
from random import choice
from random import randint
from random import random

from src.game.player import Player
from src.game.board import Board

class MCTSNode:

    def __init__(self, board, move=None, parent=None, constant=1.41, isX=True):
        self.board = copy.deepcopy(board)
        self.move = move
        self.parent = parent
        self.constant = constant
        self.isX = isX
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = Player(isX, "MCTS").getPossibleMoves(self.board)

    def select(self):
        return max(self.children, key=lambda c: (c.wins / c.visits) + self.constant * math.sqrt(math.log(self.visits) / c.visits))
    
    def expand(self):
        move = self.untriedMoves.pop()
        next_board = copy.deepcopy(self.board)
        icon = 'X' if self.isX else 'O'
        next_board.playMove(icon, move)
        child_node = MCTSNode(next_board, move=move, parent=self, constant=self.constant, isX=not self.isX)
        self.children.append(child_node)
        return child_node
    
    def update(self, result):
        self.visits += 1
        if not self.isX: 
            self.wins += result
        else:
            self.wins += (1.0 - result)
        if self.parent:
            self.parent.update(result)

    def is_fully_expanded(self):
        return len(self.untriedMoves) == 0

    def is_terminal(self):
        return self.board.state != ' '

    def rollout(self):
        tempBoard = copy.deepcopy(self.board)
        currentIsX = self.isX
        while tempBoard.state == ' ':
            moves = Player(currentIsX, "sim").getPossibleMoves(tempBoard)
            if not moves or moves == ["tie"]:
                tempBoard.state = "Game ends on a tie!"
                break
            move = choice(moves)
            icon = 'X' if currentIsX else 'O'
            tempBoard.playMove(icon, move)
            currentIsX = not currentIsX
        if "X's win" in tempBoard.state: return 1.0
        if "O's win" in tempBoard.state: return 0.0
        return 0.5