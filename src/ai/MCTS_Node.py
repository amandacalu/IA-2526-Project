import copy
import math
from random import choice
import numpy as np
import random



################## classe tabuleiro #############################
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
################# classe jogador ###############
class Player: #cria uma classe chamada 'Player'
    def __init__(self, isX: bool): #inicia um player - 'X' = MAX
        self.isX = isX

    def getPossibleMoves(self, board): #função que retorna possíveis jogadas
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

    def turn(self, board, printer=True): 
        
        """ Essa função está aqui apenas de assinatura, 
            a sua implementação vai variar dependendo da subclasse que vem a seguir"""

        raise NotImplementedError("A subclasse deve implementar o método turn!")

    def __str__(self): #imprime o player
        return 'X' if self.isX else 'O'
############# subclasse jogador humano #####################
class HumanPlayer(Player):
    def turn(self, board, printer=True):
        if printer:
            print(f"\n{self}'s turn")
            # Mostramos os movimentos possíveis para ajudar o humano
            #print(f"Possíveis tuplas (backend): {self.getPossibleMoves(board)}")
            
        while True:
            try:
                col = int(input("Escolha a coluna (1-7): "))
                tipo = input("Deseja (D)rop ou (P)op out? ").strip().upper()
                
                if tipo == 'P':
                    # No seu backend, PopOut é sempre linha 0
                    move = (0, col)
                elif tipo == 'D':
                    # Para o Drop, precisamos descobrir qual é a linha livre 
                    # usando a lógica que você já tem no getPossibleMoves
                    possiveis = self.getPossibleMoves(board)
                    # Filtra os movimentos que são Drop (linha > 0) para a coluna escolhida
                    move_encontrado = [m for m in possiveis if m[0] > 0 and m[1] == col]
                    
                    if move_encontrado:
                        move = move_encontrado[0]
                    else:
                        print("Coluna cheia! Não é possível dar Drop aqui.")
                        continue
                else:
                    print("Tipo inválido! Digite 'D' para Drop ou 'P' para Pop.")
                    continue

                # Agora testamos se essa tupla gerada é legal
                if board.isLegal(self.isX, move):
                    board.playMove(str(self), move)
                    return move
                else:
                    print(f"A jogada {tipo} na coluna {col} não é permitida pelas regras.")
            
            except ValueError:
                print("Entrada inválida! Digite apenas números para a coluna.")
################# MCTS Classico ################################
def mcts_base(rootBoard, isX: bool, iterations=10000, constant=1.41):
    
    # variavel responsavel por guardar o estado atual
    rootNode = MCTSNode(rootBoard, None, None, constant, isX)

    for _ in range(iterations):                   
        node = rootNode

        # Seleção
        while node.is_fully_expanded() and not node.is_terminal():
            node = node.select()

        # Expansão
        if not node.is_terminal():
            node = node.expand()
        
        # Simulação
        result = node.rollout()

        # BackPropagation
        node.update(result)

    best_move_node = max(rootNode.children, key=lambda c: c.visits)
    
    return best_move_node.move, best_move_node.move
############ subclasse MCTS player ####################
class MCTSPlayer(Player):
    def turn(self, board, printer=True):
        if printer:
            print(f"{self}'s turn (MCTS pensando...)")
        
        move = mcts_base(board, self.isX, 10000)
        
        board.playMove(str(self), move[0]) 
        return move[1]

######### NO MCTS ###############
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
        self.untriedMoves = MCTSPlayer(isX).getPossibleMoves(self.board)

    def ucb1(self, child):
        """Calcula o valor UCB1 para um filho específico."""
        exploitation = child.wins / child.visits
        exploration = self.constant * math.sqrt(math.log(self.visits) / child.visits)
        return exploitation + exploration

    def best_child(self):
        """Retorna o filho com o maior valor UCB1."""
        return max(self.children, key=self.ucb1)

    def select(self):
        """
        Navega pela árvore usando UCB1. 
        Este método é chamado na fase 1 do MCTS.
        """
        return self.best_child()


    def expand(self):
        move = self.untriedMoves.pop()
        next_board = copy.deepcopy(self.board)
        icon = 'X' if self.isX else 'O'
        next_board.playMove(icon, move)
        # Ao criar o filho, passamos a mesma constante de exploração
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
        board_x, board_o = self.to_bitboard(self.board.board)
        current_x_turn = self.isX
        all_cells_mask = 0b111111_111111_111111_111111_111111_111111_111111
        while True:
            moves = self.get_bit_moves(board_x, board_o, current_x_turn)
            if not moves: return 0.5
            move_bit, is_pop = choice(moves)
            if is_pop:
                board_x, board_o = self.apply_bit_pop(board_x, board_o, move_bit)
            else:
                if current_x_turn: board_x |= move_bit
                else: board_o |= move_bit
            
            x_wins = self.check_bit_win(board_x)
            o_wins = self.check_bit_win(board_o)
            
            if x_wins and o_wins: return 0.5
            if x_wins: return 1.0
            if o_wins: return 0.0
            if (board_x | board_o) == all_cells_mask: return 0.5
            current_x_turn = not current_x_turn

    def to_bitboard(self, grid):
        board_x = 0
        board_o = 0
        for c in range(7):
            for r in range(6):
                shift = c * 7 + r
                if grid[5-r, c] == 'X':
                    board_x |= (1 << shift)
                elif grid[5-r, c] == 'O':
                    board_o |= (1 << shift)
        return board_x, board_o
    
    def get_bit_moves(self, board_x, board_o, isX):
        moves = []
        occupied = board_x | board_o
        for c in range(7):
            bottom_bit = 1 << (c * 7)
            if isX:
                if board_x & bottom_bit: moves.append((bottom_bit, True))
            else:
                if board_o & bottom_bit: moves.append((bottom_bit, True))
            top_bit = 1 << (c * 7 + 5)
            if not (occupied & top_bit):
                column_mask = 0b111111 << (c * 7)
                empty_in_col = (~occupied) & column_mask
                lowest_empty = empty_in_col & -empty_in_col
                moves.append((lowest_empty, False))
        return moves
    
    def apply_bit_pop(self, board_x, board_o, move_bit):
        col_idx = 0
        temp_bit = move_bit
        while temp_bit > 0b111111:
            temp_bit >>= 7
            col_idx += 1
        col_mask = 0b111111 << (col_idx * 7)
        bits_above_mask = (col_mask ^ move_bit) & (-(move_bit << 1))
        new_x = (board_x & ~col_mask) | ((board_x & bits_above_mask) >> 1)
        new_o = (board_o & ~col_mask) | ((board_o & bits_above_mask) >> 1)
        return new_x, new_o

    def check_bit_win(self, bitboard):
        m = bitboard & (bitboard >> 7)
        if m & (m >> 14): return True
        m = bitboard & (bitboard >> 1)
        if m & (m >> 2): return True
        m = bitboard & (bitboard >> 6)
        if m & (m >> 12): return True
        m = bitboard & (bitboard >> 8)
        if m & (m >> 16): return True
        return False
############# humano vs humano ################
print("--- Humano Vs Humano ---")
playerX = HumanPlayer(isX=True)
playerO = HumanPlayer(isX=False)
board = Board()

print(board)
while board.state == ' ':
    playerX.turn(board)
    print(board)
    if board.state != ' ':
        break
    playerO.turn(board)
    print(board)
print(board.state)

#################### player vs bot #####################
import random 
print("--- Humano Vs MCTS ---")
if random.randint(0, 1) == 0:
    playerX = HumanPlayer(isX=True)
    playerO = MCTSPlayer(isX=False)
else:
    playerX = MCTSPlayer(isX=True)
    playerO = HumanPlayer(isX=False)

board = Board()
print(board)
while board.state == ' ':
    playerX.turn(board)
    print(board)
    if board.state != ' ':
        break
    playerO.turn(board)
    print(board)
print(board.state)