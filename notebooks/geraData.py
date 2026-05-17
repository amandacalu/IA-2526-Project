import csv
import os
import numpy as np
import copy
import random
import math
import time
import multiprocessing


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
    
class Player: #cria uma classe chamada 'Player'
    def __init__(self, isX: bool): #inicia um player - 'X' = MAX
        self.isX = isX

    def getPossibleMoves(self, board):
        moves = []
        
        # 1. Verifica Pop Moves (Sempre avalia a linha inferior)
        for i in range(1, 8):
            if (board.board[5][i - 1] == 'X' and self.isX) or (board.board[5][i - 1] == 'O' and not self.isX):
                moves.append((0, i))
                
        # 2. Verifica Drop Moves (Apenas se houver espaço vazio)
        if board.empty > 0:
            for i in range(1, 8):
                for j in range(1, 7):
                    if board.board[6 - j][i - 1] == ' ':
                        moves.append((j, i))
                        break
        
        # 3. Regra do Tabuleiro Cheio
        # Se encheu, o jogador TEM a opção de declarar empate,
        # concorrendo com as opções de Pop (se ele tiver peças na base)
        if board.empty == 0:
            moves.append("tie") 
            
        # Tratamento de segurança extremo: se não tem espaço e não tem pop
        if len(moves) == 0:
            moves.append("tie")
            
        return moves

    def turn(self, board, printer=True): 
        
        """ Essa função está aqui apenas de assinatura, 
            a sua implementação vai variar dependendo da subclasse que vem a seguir"""

        raise NotImplementedError("A subclasse deve implementar o método turn!")

    def __str__(self): #imprime o player
        return 'X' if self.isX else 'O'
    
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
        exploration = self.constant * np.sqrt(np.log(self.visits) / child.visits)
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
            move_bit, is_pop = random.choice(moves)
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

class MCTSPlayer(Player):

    def __init__(self, isX, name="Bot", config=None):
        super().__init__(isX)
        self.name = name
        # Config padrão: tudo desligado (Clássico)
        self.config = config if config else {
            "bias": False, "fpu": False, "smart": False, "iter": 5000
        }

    def turn(self, board, printer=True):
        if printer: print(f"[{self.name}] ({'X' if self.isX else 'O'}) pensando com config: {self.config}")
        
        # Chama a função mcts_buffed passando as flags da config
        move = mcts_buffed(board, self.isX, 
                           iterations=self.config.get("iter", 5000),
                           bias=self.config["bias"],
                           fpu=self.config["fpu"],
                           smart=self.config["smart"])
        
        board.playMove(str(self), move[0]) 
        return move[1]
    
def mcts_buffed(rootBoard, isX, iterations, bias, fpu, smart, max_children=None, constant=0.8):
    root = MCTSNodeBuffed(
        rootBoard, 
        isX=isX, 
        constant=constant,
        use_bias=bias, 
        use_fpu=fpu, 
        use_smart_rollout=smart, 
        max_children=max_children
    )
    
    for _ in range(iterations):
        node = root
        
        while node.is_fully_expanded() and not node.is_terminal():
            node = node.select()
            
        if not node.is_terminal():
            node = node.expand()
            
        result = node.rollout()
        node.update(result)
    
    best_child = max(root.children, key=lambda c: c.visits)
    
    # VOLTAMOS PARA O RETORNO DUPLICADO! 
    # Assim o seu MCTSPlayer original funciona perfeitamente sem precisar alterar nada nele.
    return best_child.move, best_child.move

class MCTSNodeBuffed(MCTSNode):
    # O prunig voltou para a assinatura para não dar erro no seu código atual
    def __init__(self, board, move=None, parent=None, constant=0.8, isX=True, 
                 use_bias=False, use_fpu=False, use_smart_rollout=False, max_children=None):
        
        super().__init__(board, move, parent, constant, isX)
        
        self.use_bias = use_bias
        self.use_fpu = use_fpu
        self.use_smart_rollout = use_smart_rollout
        self.max_children = max_children
        
        # O REQUISITO DO PROFESSOR: Limitando o número de filhos avaliados
        if self.max_children and len(self.untriedMoves) > self.max_children:
            self.untriedMoves.sort(key=lambda m: (m == 0, abs(4 - m[1])))
            self.untriedMoves = self.untriedMoves[:self.max_children]

        self.h_value = self.calculate_heuristic() if use_bias else 0

    def select(self):
        # Obriga o nó buffado a usar a matemática nova
        return max(self.children, key=lambda c: self.ucb1(c))

    def calculate_heuristic(self):
        score = 0
        if self.move:
            col = self.move[1]
            if col == 4: score += 0.2
            elif col in [3, 5]: score += 0.1 
        return score

    def ucb1(self, child):
        # TRATAMENTO FPU CORRIGIDO
        if child.visits == 0:
            if self.use_fpu:
                return (self.wins / self.visits) if self.visits > 0 else 0.5
            else:
                return float('inf')

        exploitation = child.wins / child.visits
        exploration = self.constant * math.sqrt(math.log(self.visits) / child.visits)
        
        bias = 0
        if self.use_bias:
            bias = self.h_value / (child.visits + 1)
            
        return exploitation + exploration + bias

    def rollout(self):
        if not self.use_smart_rollout:
            return super().rollout() 
        
        board_x, board_o = self.to_bitboard(self.board.board)
        curr_x = self.isX
        for _ in range(50): 
            moves = self.get_bit_moves(board_x, board_o, curr_x)
            if not moves: break
            
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
                               self.use_bias, self.use_fpu, self.use_smart_rollout, self.max_children)
        self.children.append(child)
        return child



config_classico = {"bias": False, "fpu": False, "smart": False, "iter": 10000}
config_bufado = {"bias": True, "fpu": True, "smart": True, "max_children": 6, "iter": 8000}


def trabalhador_dataset(id_processo, horas_limite):
    print(f"--- [Processo {id_processo}] Iniciando geração (Separando Vencedores e Perdedores) ---")
    
    caminho_vencedores = f'../data/raw/MCTS_Winners_data_{id_processo}.csv'
    caminho_perdedores = f'../data/raw/MCTS_Losers_data_{id_processo}.csv'
    
    os.makedirs(os.path.dirname(caminho_vencedores), exist_ok=True)
    
    if random.randint(0, 1) == 1:
        playerX = MCTSPlayer(isX=True, name="Clássico", config=config_classico)
        playerO = MCTSPlayer(isX=False, name="Buffado", config=config_bufado)
    else:
        playerX = MCTSPlayer(isX=True, name="Buffado", config=config_bufado)
        playerO = MCTSPlayer(isX=False, name="Clássico", config=config_classico)
    
    header = ["isX"] + [f"c{i}" for i in range(42)] + ["target"]
    
    with open(caminho_vencedores, 'w', newline='') as f_win, open(caminho_perdedores, 'w', newline='') as f_lose:
        writer_win = csv.writer(f_win)
        writer_lose = csv.writer(f_lose)
        writer_win.writerow(header)
        writer_lose.writerow(header)
        
    start_time = time.time()
    tempo_limite_segundos = horas_limite * 60 * 60
    games_played = 0
    
    while time.time() - start_time < tempo_limite_segundos:
        board = Board()
        
        moves_X = [] 
        moves_O = [] 
        
        while board.state == ' ':
            storedBoard = copy.deepcopy(board.board)
            
            if board.empty > 38:
                moves = playerX.getPossibleMoves(board)
                move = random.choice(moves)
                board.playMove(str(playerX), move)
            else:
                move = playerX.turn(board, False)
            
            newRowX = [1]
            for r in range(6): 
                for c in range(7):
                    if storedBoard[r][c] == "X":
                        newRowX.append(1)
                    elif storedBoard[r][c] == "O":
                        newRowX.append(-1)
                    else:
                        newRowX.append(0)
            newRowX.append(move)
            moves_X.append(newRowX)
            
            if board.state != ' ':
                break
                
            storedBoard = copy.deepcopy(board.board)
            
            if board.empty > 38:
                moves = playerO.getPossibleMoves(board)
                move = random.choice(moves)
                board.playMove(str(playerO), move)
            else:
                move = playerO.turn(board, False)
            
            newRowO = [0]
            for r in range(6):
                for c in range(7):
                    if storedBoard[r][c] == "O":
                        newRowO.append(-1)
                    elif storedBoard[r][c] == "X":
                        newRowO.append(1)
                    else:
                        newRowO.append(0)
            newRowO.append(move)
            moves_O.append(newRowO)
            
        
        if "X's win" in board.state:
            with open(caminho_vencedores, 'a', newline='') as f_win, open(caminho_perdedores, 'a', newline='') as f_lose:
                csv.writer(f_win).writerows(moves_X)
                csv.writer(f_lose).writerows(moves_O)
                
        elif "O's win" in board.state:
            with open(caminho_vencedores, 'a', newline='') as f_win, open(caminho_perdedores, 'a', newline='') as f_lose:
                csv.writer(f_win).writerows(moves_O)
                csv.writer(f_lose).writerows(moves_X)
                
            
        games_played += 1
        elapsed_time = time.time() - start_time
        print(f"[Processo {id_processo}] Jogo {games_played} concluído. Tempo: {elapsed_time/3600:.2f}/{horas_limite:.2f}h | Resultado: {board.state}")

    print(f"\n[Processo {id_processo}] Concluído!")

def gerar_datasets_paralelos(horas=7, num_processos=7):
    processos = []
    
    for i in range(num_processos):
        id_proc = chr(65 + i) 
        
        p = multiprocessing.Process(target=trabalhador_dataset, args=(id_proc, horas))
        processos.append(p)
        p.start()
        print(f"Processo {id_proc} iniciado.")
    
    for p in processos:
        p.join()
    
    print("\nTODOS OS PROCESSOS FORAM CONCLUÍDOS COM SUCESSO!")


if __name__ == '__main__':
    import multiprocessing 
    
    multiprocessing.set_start_method('fork', force=True) 
    
    gerar_datasets_paralelos(horas=17, num_processos=7)

