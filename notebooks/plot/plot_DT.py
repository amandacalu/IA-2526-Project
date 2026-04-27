
import matplotlib.pyplot as plt
import numpy as np
####### Desenha imagem da arvore ###############################
def desenhar(arvore):
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.axis('off')
    
    def plot_node(node, pos=(0.5, 1.0), largura=1.0):
        estilo_no = dict(boxstyle="round,pad=0.3", fc="#e1f5fe", ec="#01579b", lw=1)
        estilo_folha = dict(boxstyle="round,pad=0.3", fc="#e8f5e9", ec="#2e7d32", lw=1)
        
        if not isinstance(node, dict):
            ax.annotate(node, xy=pos, xytext=pos, bbox=estilo_folha, ha='center', fontsize=11)
            return

        atrib = list(node.keys())[0]
        ax.annotate(atrib, xy=pos, xytext=pos, bbox=estilo_no, ha='center', va='center', fontsize=12, weight='bold')

        ramos = node[atrib]
        num_ramos = len(ramos)
        espaco_h = largura / num_ramos
        x_ini = pos[0] - largura / 2 + espaco_h / 2

        for i, (valor, sub) in enumerate(ramos.items()):
            px, py = x_ini + i * espaco_h, pos[1] - 0.20
            ax.plot([pos[0], px], [pos[1], py], 'k-', lw=1, alpha=0.5, zorder=1)
            
            # Limpa o texto do ramo (remove \u00e9, etc)
            label_ramo = str(valor).encode('utf-8').decode('utf-8')
            ax.text((pos[0]+px)/2, (pos[1]+py)/2, label_ramo, fontsize=10, ha='center', backgroundcolor='white')
            
            plot_node(sub, pos=(px, py), largura=espaco_h)

    plot_node(arvore)
    plt.tight_layout()
    plt.show()

    ######## Desenha grafico de disperção do iris_discretizado (petalas) ###########

def plot_dispersao(df):
    """Gera o gráfico de dispersão com jitter para dados discretos."""
    # Configura o tamanho e estilo
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Mapeamento para as cores e posições
    cores = {'Iris-setosa': '#e74c3c', 'Iris-versicolor': '#3498db', 'Iris-virginica': '#27ae60'}
    mapeamento = {'Pequeno': 0, 'Médio': 1, 'Grande': 2}
    
    # Loop para plotar cada classe com um leve ruído (jitter)
    for especie, grupo in df.groupby('class'):
        # Adiciona jitter para os pontos não ficarem um em cima do outro
        x = grupo['petallength'].map(mapeamento).astype(float) + np.random.uniform(-0.15, 0.15, len(grupo))
        y = grupo['petalwidth'].map(mapeamento).astype(float) + np.random.uniform(-0.15, 0.15, len(grupo))
        
        ax.scatter(x, y, label=especie, color=cores[especie], alpha=0.6, s=70, edgecolors='white', linewidth=0.5)

    # Configura os nomes nos eixos
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(['Pequeno', 'Médio', 'Grande'])
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(['Pequeno', 'Médio', 'Grande'])
    
    # Perfumaria
    ax.set_xlabel('Comprimento da Pétala', fontsize=12)
    ax.set_ylabel('Largura da Pétala', fontsize=12)
    ax.set_title('Dispersão das Espécies (Dados Discretizados)', fontsize=14, pad=15)
    ax.legend(frameon=True, facecolor='white', loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    plt.show()


######## Desenha grafico de disperção do iris_discretizado (sepalas) ###########

def plot_dispersao_sepal(df):
    """Gera o gráfico de dispersão com jitter para dados discretos."""
    # Configura o tamanho e estilo
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Mapeamento para as cores e posições
    cores = {'Iris-setosa': '#e74c3c', 'Iris-versicolor': '#3498db', 'Iris-virginica': '#27ae60'}
    mapeamento = {'Pequeno': 0, 'Médio': 1, 'Grande': 2}
    
    # Loop para plotar cada classe com um leve ruído (jitter)
    for especie, grupo in df.groupby('class'):
        # Adiciona jitter para os pontos não ficarem um em cima do outro
        x = grupo['sepallength'].map(mapeamento).astype(float) + np.random.uniform(-0.15, 0.15, len(grupo))
        y = grupo['sepalwidth'].map(mapeamento).astype(float) + np.random.uniform(-0.15, 0.15, len(grupo))
        
        ax.scatter(x, y, label=especie, color=cores[especie], alpha=0.6, s=70, edgecolors='white', linewidth=0.5)

    # Configura os nomes nos eixos
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(['Pequeno', 'Médio', 'Grande'])
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(['Pequeno', 'Médio', 'Grande'])
    
    # Perfumaria
    ax.set_xlabel('Comprimento da Sépala', fontsize=12)
    ax.set_ylabel('Largura da Sépala', fontsize=12)
    ax.set_title('Dispersão das Espécies (Dados Discretizados)', fontsize=14, pad=15)
    ax.legend(frameon=True, facecolor='white', loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    plt.show()


 ################ Desenha grafico da dispersao x escolha da arvore de decisão


def plot_fronteiras_id3(df, arvore):
    """
    Gera o gráfico de dispersão e desenha as fronteiras de decisão da árvore.
    Considera os dois principais atributos usados na árvore: Petal Length e Petal Width.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # --- Passo 1: O gráfico de dispersão com jitter (o mesmo de antes) ---
    cores = {'Iris-setosa': '#e74c3c', 'Iris-versicolor': '#3498db', 'Iris-virginica': '#27ae60'}
    mapeamento = {'Pequeno': 0, 'Médio': 1, 'Grande': 2}
    inv_mapeamento = {0: 'Pequeno', 1: 'Médio', 2: 'Grande'}
    
    for especie, grupo in df.groupby('class'):
        x = grupo['petallength'].map(mapeamento).astype(float) + np.random.uniform(-0.15, 0.15, len(grupo))
        y = grupo['petalwidth'].map(mapeamento).astype(float) + np.random.uniform(-0.15, 0.15, len(grupo))
        ax.scatter(x, y, label=especie, color=cores[especie], alpha=0.5, s=70, zorder=3)

    # --- Passo 2: Desenhar as fronteiras baseadas na árvore (Teoria) ---
    
    # Fronteira 1: O ID3 escolheu 'petalwidth' como primeiro nó.
    # O corte principal foi: Se petalwidth é Pequeno, é Setosa.
    # A fronteira é a linha horizontal entre o nível 'Pequeno' (0) e 'Médio' (1) em petalwidth (eixo Y).
    ax.axhline(y=0.5, color='black', linestyle='--', linewidth=2, zorder=2)
    ax.text(-0.4, 0.55, 'Pétala Larga > Pequeno?', fontsize=10, color='black', weight='bold')

    # Fronteira 2: O próximo nó da sua árvore foi 'petallength' (dentro de petalwidth > Pequeno).
    # O corte foi: Se petallength é Médio, é Versicolor.
    # A fronteira é a linha vertical entre 'Pequeno' (0) e 'Médio' (1) e também entre 'Médio' (1) e 'Grande' (2) em petallength (eixo X).
    # Como a Setosa já foi separada, desenhamos apenas para os níveis acima (Médio e Grande em Y).
    
    # Corte entre Pequeno e Médio
    ax.axvline(x=0.5, ymin=0.25, ymax=1.0, color='#34495e', linestyle=':', linewidth=1.5, zorder=2)
    # Corte entre Médio e Grande
    ax.axvline(x=1.5, ymin=0.25, ymax=1.0, color='#34495e', linestyle=':', linewidth=1.5, zorder=2)
    ax.text(0.55, 1.0, 'Pétala Longa = Médio?', fontsize=9, color='#34495e')

    # --- Passo 3: Configuração dos Eixos ---
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(['Pequeno', 'Médio', 'Grande'])
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(['Pequeno', 'Médio', 'Grande'])
    
    # Limites para não cortar os nomes
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(-0.5, 2.5)

    # Perfumaria
    ax.set_xlabel('Comprimento da Pétala', fontsize=12)
    ax.set_ylabel('Largura da Pétala', fontsize=12)
    ax.set_title('Fronteiras de Decisão da Árvore (ID3) no Espaço dos Dados', fontsize=14, pad=15)
    ax.legend(title="Espécies", frameon=True, facecolor='white', loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.2)
    
    plt.tight_layout()
    plt.show()

#############Plot de decisions bondaries ###############################
import matplotlib.patches as mpatches

def plot_decision_boundaries(df, arvore, classificador_func):
    """
    Pinta o fundo do gráfico com as decisões da árvore.
    df: seu dataframe de treino/teste
    arvore: o dicionário da árvore
    classificador_func: a sua função 'classificador'
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 1. Mapeamentos
    mapeamento = {'Pequeno': 0, 'Médio': 1, 'Grande': 2}
    inv_mapeamento = {0: 'Pequeno', 1: 'Médio', 2: 'Grande'}
    cores_fundo = {'Iris-setosa': '#ffcccc', 'Iris-versicolor': '#cce5ff', 'Iris-virginica': '#ccffcc'}
    cores_pontos = {'Iris-setosa': 'red', 'Iris-versicolor': 'blue', 'Iris-virginica': 'green'}

    # 2. Criar a grade (grid) de fundo
    # Vamos criar pequenos quadrados para representar as combinações de atributos
    for x_val in [0, 1, 2]:
        for y_val in [0, 1, 2]:
            # Criamos um "exemplo" fictício para a árvore classificar
            exemplo_ficticio = {
                'petallength': inv_mapeamento[x_val],
                'petalwidth': inv_mapeamento[y_val],
                'sepallength': 'Médio', # Valores neutros para os outros atributos
                'sepalwidth': 'Médio'
            }
            
            # Pergunta para a SUA árvore qual é a classe desse quadrante
            classe_prevista = classificador_func(exemplo_ficticio, arvore)
            
            # Pinta o quadrante com a cor da classe (o fundo)
            cor = cores_fundo.get(classe_prevista, '#ffffff')
            rect = mpatches.Rectangle((x_val-0.5, y_val-0.5), 1, 1, color=cor, zorder=1)
            ax.add_patch(rect)

    # 3. Plotar os pontos reais com Jitter por cima
    for especie, grupo in df.groupby('class'):
        xj = grupo['petallength'].map(mapeamento).astype(float) + np.random.uniform(-0.15, 0.15, len(grupo))
        yj = grupo['petalwidth'].map(mapeamento).astype(float) + np.random.uniform(-0.15, 0.15, len(grupo))
        ax.scatter(xj, yj, label=especie, color=cores_pontos[especie], edgecolors='k', s=60, zorder=2)

    # 4. Ajustes de eixos
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(['Pequeno', 'Médio', 'Grande'])
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(['Pequeno', 'Médio', 'Grande'])
    
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(-0.5, 2.5)
    ax.set_xlabel('Comprimento da Pétala')
    ax.set_ylabel('Largura da Pétala')
    ax.set_title('Regiões de Decisão da Árvore')
    ax.legend(loc='upper left', title="Espécies")
    
    plt.tight_layout()
    plt.show()