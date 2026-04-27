from ID3 import entropia, ganho_informacao, my_ID3
#1) Discretizaçao do iris
import pandas as pd

#1.1) Ler o arquivo original
caminho_original = "/home/amanux/4sem/ia/tp/IA-2526-Project/data/raw/iris.csv"
df = pd.read_csv(caminho_original)

# 1.2) Remover a coluna ID (se ela existir)
# O parâmetro 'errors=ignore' serve para não dar erro caso o nome seja diferente ou não exista
df = df.drop(['id', 'ID', 'Unnamed: 0'], axis=1, errors='ignore')

# 1.3) Discretizar as colunas numéricas
colunas_features = ['sepallength', 'sepalwidth', 'petallength', 'petalwidth']

for col in colunas_features:
    # Criamos os baldes (Pequeno, Médio, Grande)
    df[col] = pd.qcut(df[col], 3, labels=["Pequeno", "Médio", "Grande"])

# 1.4) Salvar o novo dataset em um novo arquivo CSV
# index=False evita que o pandas crie uma coluna extra de números no início do arquivo
caminho_destino = "/home/amanux/4sem/ia/tp/IA-2526-Project/data/processed/iris_discretizado.csv"
df.to_csv(caminho_destino, index=False)

print(f"Sucesso! Arquivo gerado em: {caminho_destino}")
print(df.head()) # Mostra as primeiras linhas para conferir

X = df.drop('class', axis=1) #pega a discretizaçao acima e atribui a X (tudo menos 'class')
y = df['class']

DT_final = my_ID3(df,X,y)
import json
print(json.dumps(DT_final, indent=4))

import numpy as np
nome_classes, contagem = np.unique(y,return_counts=True)
print(nome_classes)
print(contagem)