import board
import player
import mcts
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

##################### hum vc mcts buffado novo ###############
import random 

print("\n--- Configuração de Partida: Humano Vs MCTS Buffado ---")

# 1. Definir as heurísticas do Bot de forma atômica
def get_custom_config():
    print("\nConfigure as habilidades do MCTS:")
    return {
        "bias":    input("  > Ativar Progressive Bias? (s/n): ").lower() == 's',
        "fpu":     input("  > Ativar FPU (First Play Urgency)? (s/n): ").lower() == 's',
        "smart":   input("  > Ativar Smart Rollout (Win/Loss Detection)? (s/n): ").lower() == 's',
        "pruning": input("  > Ativar Pruning (Ordenação de movimentos)? (s/n): ").lower() == 's',
        "iter":    int(input("  > Número de iterações (ex: 5000): "))
    }

config_do_bot = get_custom_config()

# 2. Sorteio de quem começa (X ou O)
if random.randint(0, 1) == 0:
    print("\n[VOCÊ É O 'X' E COMEÇA!]")
    playerX = HumanPlayer(isX=True)
    playerO = MCTSPlayer(isX=False, name="MCTS_Campeao", config=config_do_bot)
else:
    print("\n[O BOT É O 'X' E COMEÇA!]")
    playerX = MCTSPlayer(isX=True, name="MCTS_Campeao", config=config_do_bot)
    playerO = HumanPlayer(isX=False)

# 3. Execução do Jogo (O loop permanece quase igual, mas usa os players configurados)
board = Board()
print(board)

while board.state == ' ':
    # Turno do Jogador X
    playerX.turn(board)
    print(board)
    if board.state != ' ':
        break
    
    # Turno do Jogador O
    playerO.turn(board)
    print(board)

print("\nFIM DE JOGO!")
print(f"Resultado: {board.state}")
########### bot vs bot novo ###############
import time

print("--- MCTS Clássico Vs MCTS Buffado ---")

# Configuração do Bot Clássico (Baseline)
config_classico = {
    "bias": False, "fpu": False, "smart": False, "pruning": False, "iter": 5000
}

# Configuração do Bot Buffado (Campeão em teste)
config_buffado = {
    "bias": True, "fpu": True, "smart": True, "pruning": True, "iter": 5000
}

# Instanciação
playerX = MCTSPlayer(isX=True, name="Clássico", config=config_classico)
playerO = MCTSPlayer(isX=False, name="Buffado", config=config_buffado)

board = Board()
print(board)

while board.state == ' ':
    # Turno do Bot X
    start = time.time()
    playerX.turn(board, printer=True)
    print(f"Tempo de pensamento: {time.time() - start:.2f}s")
    print(board)
    if board.state != ' ': break
    
    # Turno do Bot O
    start = time.time()
    playerO.turn(board, printer=True)
    print(f"Tempo de pensamento: {time.time() - start:.2f}s")
    print(board)

print("\nRESULTADO:")
print(board.state)