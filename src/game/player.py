import board
import mcts
import numpy as np
####class player##################
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
############## subclasse jogador bot######################
import math

class MCTSPlayer(Player):
    def __init__(self, isX, name="Bot", config=None):
        super().__init__(isX)
        self.name = name
        # Config padrão: tudo desligado (Clássico)
        self.config = config if config else {
            "bias": False, "fpu": False, "smart": False, "pruning": False, "iter": 5000
        }

    def turn(self, board, printer=True):
        if printer: print(f"[{self.name}] pensando com config: {self.config}")
        
        # Chama a função mcts_buffed passando as flags da config
        move = mcts_buffed(board, self.isX, 
                           iterations=self.config.get("iter", 5000),
                           bias=self.config["bias"],
                           fpu=self.config["fpu"],
                           smart=self.config["smart"],
                           pruning=self.config["pruning"])
        
        board.playMove(str(self), move[0]) 
        return move[1]