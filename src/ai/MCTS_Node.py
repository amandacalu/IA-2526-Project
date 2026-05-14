import copy
import math
from random import choice

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