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

lista_config = [
    # Testando com poda AGRESSIVA (Olha apenas os 5 melhores lances)
    ("Buffado (4 filhos) - 5000 iter", {"bias": True, "fpu": True, "smart": True, "max_children": 4, "iter": 5000}),
    ("Buffado (4 filhos) - 6000 iter", {"bias": True, "fpu": True, "smart": True, "max_children": 4, "iter": 6000}),
    ("Buffado (4 filhos) - 7000 iter", {"bias": True, "fpu": True, "smart": True, "max_children": 4, "iter": 7000}),
    ("Buffado (4 filhos) - 8000 iter", {"bias": True, "fpu": True, "smart": True, "max_children": 4, "iter": 8000}),

    # Testando com poda MODERADA (Olha os 8 melhores lances, ignorando só o lixo)
    ("Buffado (4 filhos) - 8000 iter", {"bias": True, "fpu": True, "smart": True, "max_children": 4, "iter": 8000}),
    ("Buffado (4 filhos) - 9000 iter", {"bias": True, "fpu": True, "smart": True, "max_children": 4, "iter": 9000}),
    ("Buffado (4 filhos) - 10000 iter", {"bias": True, "fpu": True, "smart": True, "max_children": 4, "iter": 10000}),
    ("Buffado (4 filhos) - 11000 iter", {"bias": True, "fpu": True, "smart": True, "max_children": 4, "iter": 11000})
]

# 1. Isolamos a lógica principal na função trabalhadora
def trabalhador_torneio(nome, config, num_partidas=100):
    print(f"--- [Iniciando] Torneio: {nome} ---")
    start_time = time.time()
    
    vitorias_buffado = 0
    vitorias_classico = 0
    empates = 0

    for partida in range(1, num_partidas + 1):
        board = Board()

        if random.randint(0, 1) == 1:
            playerX = MCTSPlayer(isX=True, name="Clássico", config=config_classico)
            playerO = MCTSPlayer(isX=False, name="Buffado", config=config)
            icon_buffado = 'O'
        else:
            playerX = MCTSPlayer(isX=True, name="Buffado", config=config)
            playerO = MCTSPlayer(isX=False, name="Clássico", config=config_classico)
            icon_buffado = 'X'

        while board.state == ' ':
            playerX.turn(board, printer=False)
            if board.state != ' ': break
            playerO.turn(board, printer=False)

        estado_final = board.state.lower()
        if "tie" in estado_final:
            empates += 1
        elif f"{icon_buffado.lower()}'s win" in estado_final:
            vitorias_buffado += 1
        else:
            vitorias_classico += 1
            
        # Imprime o progresso a cada 2 partidas (2.% do total)
        if partida % 2 == 0:
            print(f"⏳ [{nome}] Progresso: {partida}/{num_partidas} concluídas...")

    tempo_decorrido = (time.time() - start_time) / 60
    
    # Prepara o texto do resultado final
    texto_resultado = (
        f"\n==================================================\n"
        f"✅ Placar Final - {nome} ({tempo_decorrido:.2f} min):\n"
        f"  🏆 Vitórias do Buffado: {vitorias_buffado}/{num_partidas}\n"
        f"  💀 Vitórias do Clássico: {vitorias_classico}/{num_partidas}\n"
        f"  🤝 Empates: {empates}/{num_partidas}\n"
        f"  🎯 WinRate: {round((vitorias_buffado/num_partidas*100),2)}%\n"
        f"  🔄 Jogos:   {num_partidas}\n"
        f"==================================================\n"
    )
    
    # Abre o arquivo em modo 'a' (append) para adicionar o texto sem apagar os anteriores
    with open("resultados_torneio.txt", "a", encoding="utf-8") as arquivo:
        arquivo.write(texto_resultado)
        
    # Aviso rápido no terminal para você saber que aquele torneio terminou e salvou
    print(f"💾 [{nome}] Finalizado! Placar salvo em 'resultados_torneio.txt'.")


# 2. A função principal que gerencia o paralelismo em lotes
def executar_torneios_em_lotes():
    lote_1 = lista_config[:4]
    lote_2 = lista_config[4:]
    
    print("\n🚀 INICIANDO LOTE 1 (Primeiras 4 configurações)...\n")
    processos_lote_1 = []
    
    for nome, config in lote_1:
        # Cria e inicia um processo para cada config do lote 1
        p = multiprocessing.Process(target=trabalhador_torneio, args=(nome, config))
        processos_lote_1.append(p)
        p.start()
        
    # Espera todos do lote 1 terminarem
    for p in processos_lote_1:
        p.join()
        
    print("\n🚀 LOTE 1 CONCLUÍDO! INICIANDO LOTE 2 (Últimas 4 configurações)...\n")
    processos_lote_2 = []
    
    for nome, config in lote_2:
        # Cria e inicia um processo para cada config do lote 2
        p = multiprocessing.Process(target=trabalhador_torneio, args=(nome, config))
        processos_lote_2.append(p)
        p.start()
        
    # Espera todos do lote 2 terminarem
    for p in processos_lote_2:
        p.join()
        
    print("\n🏁 TODOS OS TORNEIOS FORAM CONCLUÍDOS COM SUCESSO!")

if __name__ == '__main__':
    # Usando exatamente o método que você validou no Arch
    multiprocessing.set_start_method('fork', force=True) 
    
    # Roda a função
    executar_torneios_em_lotes()