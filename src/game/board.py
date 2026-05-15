################## classe tabuleiro #############################
import numpy as np
class Board: #cria uma classe chamada 'Board'

    def __init__(self): #função que inicia o tabuleiro
        self.board = np.full((6, 7), ' ', dtype=str) #cria um tabuleiro de 7 colunas e 6 linhas
        self.empty = 42 #define se está vazio - são 42 slots (7x6)
        self.record = dict() #guarda estado num dicionario
        self.record[repr(self)] = 1 #marca que o estado ocorreu
        self.state = ' ' 

    def isLegal(self, isX: bool, move: tuple[int, int]): #função que garante que as jogadas são validas
        r, c = move[0], move[1] - 1
        if r == 0:
            return ((isX and self.board[5, c] == 'X') or (not isX and self.board[5, c] == 'O'))
        if r == 1:
            return self.board[6 - r, c] == ' '
        return (self.board[7 - r, c] != ' ' and self.board[6 - r, c] == ' ')
    
    def playMove(self, icon: str, move: tuple[int, int]): #função que efetiva jogada (se valida)
        if move == "tie":
            self.state = "Game ends on a tie!"
            return
        r, c = move[0], move[1] - 1
        if r == 0:
            self.board[1:, c] = self.board[:-1, c]
            self.board[0, c] = ' '
            self.empty += 1
        else:
            self.board[6 - r, c] = icon
            self.empty -= 1
        current_state = repr(self)
        if current_state in self.record:
            if self.record[current_state] == 2:
                self.state = "Game ends on a tie!"
            else:
                self.record[current_state] += 1
        else:
            self.record[current_state] = 1  
        self.checkWin('O' if icon == 'X' else 'X')
        self.checkWin(icon)


    def checkWin(self, icon: str): #função que checka se houve vitória
        b = (self.board == icon)
        if np.any(b[:, :-3] & b[:, 1:-2] & b[:, 2:-1] & b[:, 3:]):
            self.state = f"Game ends on {icon}'s win!"
            return
        if np.any(b[:-3, :] & b[1:-2, :] & b[2:-1, :] & b[3:, :]):
            self.state = f"Game ends on {icon}'s win!"
            return
        if np.any(b[:-3, :-3] & b[1:-2, 1:-2] & b[2:-1, 2:-1] & b[3:, 3:]):
            self.state = f"Game ends on {icon}'s win!"
            return
        if np.any(b[3:, :-3] & b[2:-1, 1:-2] & b[1:-2, 2:-1] & b[:-3, 3:]):
            self.state = f"Game ends on {icon}'s win!"
            return

    def __str__(self): #função que imprime estado
        printer = "  -----------------------------\n"
        for i in range(6):
            printer += f"{6 - i} |"
            for j in range(7):
                current = self.board[i, j]
                if current in ('X', 'O'):
                    printer += f" {current} |"
                else:
                    printer += "   |"
            printer += "\n  -----------------------------\n"
        printer += "    1   2   3   4   5   6   7"
        return printer
    
    def __repr__(self): #função que efetiva estado
        return "".join(self.board.ravel())