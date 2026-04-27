# Arquivo: visualizador_arvore.py
import matplotlib.pyplot as plt

# Configurações globais de estilo
ESTILO_NO = dict(boxstyle="round,pad=0.5", fc="#D1E8FF", ec="#1C3A5A", alpha=0.9, lw=1.5)
ESTILO_FOLHA = dict(boxstyle="round,pad=0.5", fc="#C2F0C2", ec="#1E5C1E", alpha=0.9, lw=1.5)
ESTILO_SETA = dict(arrowstyle="<-", connectionstyle="arc3", color="#555555", lw=1.2)
FONTE_TEXTO = {'fontsize': 10, 'weight': 'bold', 'color': 'black'}
FONTE_RAMO = {'fontsize': 9, 'color': '#AA0000', 'style': 'italic'}

def _obter_profundidade(arvore):
    """Calcula a profundidade máxima da árvore de forma recursiva."""
    if not isinstance(arvore, dict):
        return 1
    attr = list(arvore.keys())[0]
    ramos = arvore[attr]
    if not ramos:
        return 1
    # Retorna 1 + a profundidade do ramo mais profundo
    return 1 + max(_obter_profundidade(subarvore) for subarvore in ramos.values())

def _plotar_no(ax, texto, centro, pai, estilo, fonte):
    """Desenha um nó (caixa) e a seta conectando ao nó pai."""
    # Desenha a caixa de texto
    ax.text(centro[0], centro[1], texto, ha='center', va='center', bbox=estilo, **fonte)
    
    # Desenha a seta se houver um pai
    if pai:
        ax.annotate("", xy=pai, xytext=centro, arrowprops=ESTILO_SETA)

def _desenhar_recursivo(ax, arvore, x, y, dx, pai=None):
    """Função recursiva que percorre e desenha a árvore."""
    # Se não for dicionário, é uma folha (Classe Final)
    if not isinstance(arvore, dict):
        texto_folha = f"CLASSE:\n{str(arvore)}"
        _plotar_no(ax, texto_folha, (x, y), pai, ESTILO_FOLHA, FONTE_TEXTO)
        return

    # Pega o atributo (raiz da sub-árvore atual)
    atributo = list(arvore.keys())[0]
    _plotar_no(ax, atributo, (x, y), pai, ESTILO_NO, FONTE_TEXTO)

    # Desenha os ramos para cada valor do atributo
    ramos = arvore[atributo]
    num_ramos = len(ramos)
    
    # Se não houver ramos, encerra aqui (não deveria acontecer no ID3 padrão)
    if num_ramos == 0:
        return

    # Calcula o espaçamento horizontal inicial para os filhos
    # dx é a largura total disponível, dx/2 espalha os filhos
    largura_espalhamento = dx 
    incremento_x = largura_espalhamento / (num_ramos if num_ramos > 1 else 1)
    # Define o X inicial centralizado
    x_inicial = x - (largura_espalhamento / 2) + (incremento_x / 2)
    
    for i, (valor_ramo, subarvore) in enumerate(ramos.items()):
        if num_ramos > 1:
            child_x = x_inicial + (i * incremento_x)
        else:
            child_x = x # Se for filho único, mantém na mesma linha X
            
        child_y = y - 1  # Desce um nível no eixo Y
        
        # 1. Desenha o texto do ramo (o valor do balde: Pequeno, Médio, Grande)
        # Posicionado no meio do caminho da seta
        texto_ramo_x = (x + child_x) / 2
        texto_ramo_y = (y + child_y) / 2
        ax.text(texto_ramo_x, texto_ramo_y, str(valor_ramo), ha='center', va='center', 
                bbox=dict(fc='white', ec='none', alpha=0.7, pad=0.1), **FONTE_RAMO)
        
        # 2. Chamada recursiva para desenhar o próximo nível
        # Passa dx / num_ramos para estreitar o espalhamento no próximo nível
        _desenhar_recursivo(ax, subarvore, child_x, child_y, dx / max(num_ramos, 1.5), (x, y))

def draw_dt(tree):
    """
    Função principal que configura o ambiente Matplotlib e desenha a árvore ID3.
    Use: draw_dt(sua_arvore_dict)
    """
    if not tree:
        print("Árvore vazia. Nada para plotar.")
        return
        
    profundidade = _obter_profundidade(tree)
    
    # Cria a figura com um tamanho proporcional à profundidade
    largura_fig = max(10, profundidade * 3)
    altura_fig = max(6, profundidade * 1.5)
    
    fig, ax = plt.figure(figsize=(largura_fig, altura_fig)), plt.gca()
    plt.axis('off') # Esconde os eixos X e Y (réguas de números)

    # dx_inicial controla quão longe os primeiros filhos se espalham
    dx_inicial = 8
    # y_inicial é o topo da árvore, profundidade garante espaço abaixo
    y_inicial = profundidade 
    
    # Inicia a plotagem recursiva
    _desenhar_recursivo(ax, tree, x=0, y=y_inicial, dx=dx_inicial)

    plt.title("Visualização da Árvore de Decisão ID3", fontsize=16, weight='bold', pad=20)
    
    # Ajusta os limites do gráfico automaticamente para nada ficar de fora
    ax.autoscale()
    plt.show()