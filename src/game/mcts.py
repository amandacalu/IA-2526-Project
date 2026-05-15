import copy
import math
from random import choice
import numpy as np
import random
import board, player
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
################ mcts modo buffado ###############
def mcts_buffed(rootBoard, isX, iterations, bias, fpu, smart, pruning):
    """
    Função motor que aceita as flags individuais para cada heurística.
    """
    # Criamos o nó raiz passando as configurações para o nó buffado
    root = MCTSNodeBuffed(
        rootBoard, 
        isX=isX, 
        use_bias=bias, 
        use_fpu=fpu, 
        use_smart_rollout=smart, 
        use_pruning=pruning
    )
    
    for _ in range(iterations):
        node = root
        
        # Fase 1: Seleção
        while node.is_fully_expanded() and not node.is_terminal():
            node = node.select()
            
        # Fase 2: Expansão
        if not node.is_terminal():
            node = node.expand()
            
        # Fase 3: Simulação (Rollout)
        result = node.rollout()
        
        # Fase 4: Backpropagation
        node.update(result)
    
    # Retorna o melhor movimento com base no número de visitas
    best_child = max(root.children, key=lambda c: c.visits)
    return best_child.move, best_child.move
############# no do mcts buffado - subclasse #############
class MCTSNodeBuffed(MCTSNode):
    def __init__(self, board, move=None, parent=None, constant=1.41, isX=True, 
                 use_bias=False, use_fpu=False, use_smart_rollout=False, use_pruning=False):
        super().__init__(board, move, parent, constant, isX)
        
        # Configurações Atômicas
        self.use_bias = use_bias
        self.use_fpu = use_fpu
        self.use_smart_rollout = use_smart_rollout
        self.use_pruning = use_pruning
        
        # Se Pruning estiver ativo, ordenamos os movimentos (Prioriza centro, depois Drop, depois Pop)
        if self.use_pruning:
            self.untriedMoves.sort(key=lambda m: (m[0] == 0, abs(4 - m[1])))

        # Valor heurístico para Progressive Bias
        self.h_value = self.calculate_heuristic() if use_bias else 0

    def calculate_heuristic(self):
        # Heurística simples: bônus por peças no centro e conexões de 2 ou 3
        score = 0
        icon = 'X' if not self.isX else 'O'
        # Bônus por proximidade do centro (coluna 4)
        if self.move and self.move[1] == 4: score += 0.5
        # Aqui você pode expandir para contar peças adjacentes no board
        return score

    def ucb1(self, child):
        # 1. Tratamento de FPU (First Play Urgency)
        if self.use_fpu and child.visits == 0:
            return 1000.0 # Valor alto para garantir que seja visitado ao menos uma vez rápido
        
        if child.visits == 0: return float('inf')

        exploitation = child.wins / child.visits
        exploration = self.constant * math.sqrt(math.log(self.visits) / child.visits)
        
        # 2. Progressive Bias
        bias = 0
        if self.use_bias:
            bias = self.h_value / (child.visits + 1)
            
        return exploitation + exploration + bias

    def rollout(self):
        if not self.use_smart_rollout:
            return super().rollout() # Usa o seu bitboard clássico veloz
        
        # Smart Rollout com Detecção de Vitória/Bloqueio [cite: 13, 15]
        board_x, board_o = self.to_bitboard(self.board.board)
        curr_x = self.isX
        for _ in range(50): # Limite de passos
            moves = self.get_bit_moves(board_x, board_o, curr_x)
            if not moves: break
            
            # Win/Loss Detection
            selected_move = None
            for m_bit, is_pop in moves:
                if not is_pop:
                    tx, to = (board_x | m_bit, board_o) if curr_x else (board_x, board_o | m_bit)
                    if self.check_bit_win(tx if curr_x else to):
                        selected_move = (m_bit, is_pop)
                        break
            
            move_bit, is_pop = selected_move if selected_move else random.choice(moves)
            
            if is_pop: board_x, board_o = self.apply_bit_pop(board_x, board_o, move_bit)
            else:
                if curr_x: board_x |= move_bit
                else: board_o |= move_bit
            
            if self.check_bit_win(board_x): return 1.0
            if self.check_bit_win(board_o): return 0.0
            curr_x = not curr_x
        return 0.5

    def expand(self):
        move = self.untriedMoves.pop()
        next_board = copy.deepcopy(self.board)
        next_board.playMove('X' if self.isX else 'O', move)
        child = MCTSNodeBuffed(next_board, move, self, self.constant, not self.isX,
                               self.use_bias, self.use_fpu, self.use_smart_rollout, self.use_pruning)
        self.children.append(child)
        return child