# 3) implementar e aplicar ID3
import numpy as np #importa numpy para calculos precisos matematicos

#3.1) Calculo de entropia (pagina 30 - slide 7)
def entropia(y):
    nome_classes, contagem = np.unique(y,return_counts=True) #funcao unique retorna o nome e a quantidade de cada classe
    # Iris-setosa ou Iris-versicolor ou Iris-virginica
    prob = contagem/len(y) #prob é a quantidade que uma class aparece / tamanho do dataset
    return -np.sum(prob*np.log2(prob)) #Entropia: soma de -p * log2(p) (mensura a incerteza em cima de uma alguma varivael X)

#3.2) Calculo de ganho de informaçao (pagina 31 - slide 7)
def ganho_informacao(df,atributo,y):
    entropia_total = entropia(y) #calcula a entropia H(c)
    baldes,contagens = np.unique(df[atributo],return_counts=True) #retorna os valores e quantidade de cada 'balde' dentro de uma feature em X
    entropia_condiconal = 0 #inicial em 0

    for balde in range(len(baldes)): # H(C|Atributo) ou seja a prob de Y sabendo de um atributo (de X) em especifico
        subset = df[df[atributo] == baldes[balde]] #define um subset de um atributo em X por cada balde (valores da discretizaçao)
        prob_subgrupo = contagens[balde]/len(df) #calcula a prob de um atributo em especifico aparecer no dataset
        entropia_condiconal += prob_subgrupo* entropia(subset[y]) #soma das prob de cada subgrupo * a entopia do total do subgrupo
    return entropia_total - entropia_condiconal #ganho de informaçao (slide 33 - Ganho(A) = I(C;A) = H(C)-H(C|A))
    
#3.3) implememtaçao do ID3 (implementado a partir do pseudocodigo da pagina 35 - slide 7)
def my_ID3(Examples,X,y):
    if len(np.unique(y)) == 1: #se todos os exemplos tem o mesmo valor de target retorna a root com esse valor - caso base
        return np.unique(y)[0]
    if X.empty: #se nao tem variavel independente retorna a moda de y - case base quando ja reparou todos as features
        return y.mode()[0]
    
    ganhos = [] #cria lista de ganhos
    for var_ind in X.columns: #calcula o ganho de informação de casa variavel independente 
        valor_ganho = ganho_informacao(Examples,var_ind,y.name) 
        ganhos.append(valor_ganho) #add ganho i na lista de ganhos

    indice_melhor = np.argmax(ganhos) #acha o indce da lista do maior ganho
    A = X.columns[indice_melhor] #define A como o maior dos ganhos
    #A é definido como o melhor classificador do dataset
    tree = {A: {}} #cria a root da arvore (com inmpletaçao de dicionario)
    #pega o melhor atributo A, e adiciona os baldes como chave externa
    #exemplo, se A = 'petallenhth', tree = {'petallenght" = {}}
    #tree['petallength']['Pequeno'] = 'Iris-setosa' #folha
    #tree['petallength']['Grande'] = {'sepalwidth': {}} #outro nó (sub-árvore)
    for valor in Examples[A].unique(): #itera sobre os valores possives dado a feature escolhida A
        subset = Examples[Examples[A] == valor] #faz com que o set de exemplos analisados seja Examples(vi)
        if subset.empty: #se esse subset for vazio
            tree[A][valor] = y.mode()[0] #escolhe a moda de y
        else: #cria nova  lista de var inde tirando antigo A
            novos_X = X.drop(A, axis=1) #remove o A que ja foi escolhido
            novo_y = subset[y.name]
            tree[A][valor] = my_ID3(subset,novos_X,novo_y) #chama recursivamente a funçao para os novos valores
    return tree

#3.4) define classifcador com o ID3
def classificador(exemplo,arvore):
    if not isinstance(arvore,dict): #se a arvore nao der um dict, chegamos em uma folha
        return arvore
    
    atributo = list(arvore.keys())[0] #pega o atributo que está no no da arvore
    valor_exemplo = exemplo[atributo] #pega o valor q o exemplo tem paar esse atributo

    if valor_exemplo in arvore[atributo]: #segue pelo ramo correspondente
        sub_arvore = arvore[atributo][valor_exemplo]
        return classificador(exemplo, sub_arvore)
    else: #caso o valor nao existe - !!!(talvez posso duar aqui para retornar a moda)!!!
        return "Classe Desconhecida"

            
# 4) usar randomit para gerar um novo data set de teste
# 5) analise e plotagem com matplot e seaborn

#DT - Popout
# 1) Rodar o jogo varias vezes e gerar csv
# 2) ler o dataset no pandas
# 3) discretizar os dados de treino
# 4) Aplicar ID3
# 5) novas jogadas para novos dados de teste
# 6) Analises de performance