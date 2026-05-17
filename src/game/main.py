import time
import random
from board import Board
from player import HumanPlayer, MCTSPlayer

def exibir_explicacao_heuristicas():
    print("\n--- Guia de Heurísticas Buffadas ---")
    print("1. Progressive Bias: Guia a árvore inicial com base em peças no centro.")
    print("2. FPU (First Play Urgency): Garante que novos caminhos sejam explorados rapidamente.")
    print("3. Smart Rollout: Simulações inteligentes que detectam vitórias/bloqueios imediatos.")
    print("4. Pruning: Ordena e prioriza movimentos promissores (ex: centro antes das bordas).")

def configurar_bot_custom(nome):
    print(f"\n--- Configurando {nome} ---")
    exibir_explicacao_heuristicas()
    bias = input(f"Ativar Progressive Bias para {nome}? (s/n): ").lower() == 's'
    fpu = input(f"Ativar FPU para {nome}? (s/n): ").lower() == 's'
    smart = input(f"Ativar Smart Rollout para {nome}? (s/n): ").lower() == 's'
    pruning = input(f"Ativar Pruning para {nome}? (s/n): ").lower() == 's'
    iterations = int(input(f"Número de iterações para {nome} (padrão 5000): ") or 5000)
    
    return {
        "bias": bias, "fpu": fpu, "smart": smart, 
        "pruning": pruning, "iter": iterations
    }

def loop_jogo(pX, pO, visual=True):
    jogo_board = Board()
    if visual: print(jogo_board)
    
    while jogo_board.state == ' ':
        # Turno do Jogador X
        start_time = time.time()
        pX.turn(jogo_board, printer=visual)
        duration = time.time() - start_time
        
        if visual:
            print(jogo_board)
            if isinstance(pX, MCTSPlayer):
                print(f"Tempo de resposta do Bot X: {duration:.2f}s")
        
        if jogo_board.state != ' ': break

        # Turno do Jogador O
        start_time = time.time()
        pO.turn(jogo_board, printer=visual)
        duration = time.time() - start_time
        
        if visual:
            print(jogo_board)
            if isinstance(pO, MCTSPlayer):
                print(f"Tempo de resposta do Bot O: {duration:.2f}s")
                
    if visual: print(f"\nFIM DE JOGO: {jogo_board.state}")
    return jogo_board.state

def menu_principal():
    while True:
        print("\n" + "="*40)
        print("          POPOUT - MENU PRINCIPAL")
        print("="*40)
        print("1) Human vs. Human")
        print("2) Human vs. Computer")
        print("3) Computer vs. Computer (Batalha/Análise)")
        print("0) Sair")
        
        opcao = input("\nEscolha uma opção: ")

        if opcao == '1':
            pX = HumanPlayer(isX=True)
            pO = HumanPlayer(isX=False)
            loop_jogo(pX, pO)

        elif opcao == '2':
            print("\nJogar contra:")
            print("1) MCTS Clássico (c=1.41, i=10.000)")
            print("2) MCTS Buffado (Configurável)")
            tipo_bot = input("Escolha o bot: ")
            
            if tipo_bot == '1':
                config = {"bias": False, "fpu": False, "smart": False, "pruning": False, "iter": 10000}
            else:
                config = configurar_bot_custom("Bot_Buffado")
            
            if random.randint(0, 1) == 0:
                print("\nVocê é o X (começa)!")
                pX = HumanPlayer(isX=True)
                pO = MCTSPlayer(isX=False, name="Computador", config=config)
            else:
                print("\nO Computador é o X (começa)!")
                pX = MCTSPlayer(isX=True, name="Computador", config=config)
                pO = HumanPlayer(isX=False)
            loop_jogo(pX, pO)

        elif opcao == '3':
            c1 = configurar_bot_custom("Bot 1")
            c2 = configurar_bot_custom("Bot 2")
            
            print("\nModo de Execução:")
            print("1) Jogo Único (Visual)")
            print("2) Bateria de Jogos (Análise Estatística)")
            modo = input("Escolha: ")
            
            p1 = MCTSPlayer(isX=True, name="Bot_1", config=c1)
            p2 = MCTSPlayer(isX=False, name="Bot_2", config=c2)

            if modo == '1':
                loop_jogo(p1, p2, visual=True)
            else:
                qtd = int(input("Quantas partidas deseja rodar? "))
                vitorias_p1 = 0
                vitorias_p2 = 0
                empates = 0
                tempos = []

                print(f"\nRodando {qtd} partidas... aguarde.")
                for i in range(qtd):
                    start = time.time()
                    resultado = loop_jogo(p1, p2, visual=False)
                    tempos.append(time.time() - start)
                    
                    if "X's win" in resultado: vitorias_p1 += 1
                    elif "O's win" in resultado: vitorias_p2 += 1
                    else: empates += 1
                
                print("\n" + "### ANALISE FINAL ###")
                print(f"Vitórias Bot 1 (X): {vitorias_p1} ({(vitorias_p1/qtd)*100:.1f}%)")
                print(f"Vitórias Bot 2 (O): {vitorias_p2} ({(vitorias_p2/qtd)*100:.1f}%)")
                print(f"Empates: {empates} ({(empates/qtd)*100:.1f}%)")
                print(f"Tempo médio por partida: {sum(tempos)/len(tempos):.2f}s")

        elif opcao == '0':
            break

if __name__ == "__main__":
    menu_principal()