# IA-2526-Project
Estrutura do projeto:
1) Data:
1.1) Data/Processed: Contém as informações dos dataset que tiveram alguma alteração
1.2) Data/Raw: Contém os datasets da maneira que foi gerado

2) Notebooks:
2.1) Notebooks/img: Contém as imagens utilizadas no relatório
2.2) Notebook/plot: Contém funções auxiliares definidas para gerar gráficos ao relatório
- final_submission.ipynb: Arquivo no formato Jupyter Notebook que contém o relatório final de acordo com assignment proposto
# - arena.py: Arquivo python que contém o código para disputa de MCTSs
# - geraData.py: Arquivo python que contém o código para gerar os datasets de dados de disputa dos MCTSs
# -resultados_torneio.txt: Resultado das disputas entre diversos alterações de MTCSs para análise

3) Src:
3.1) Src/DT: Contém código referente a Árvores de Decisão
- ID3.py: Código que implementa o algoritmo ID3 e seu respectivo classificador de novos exemplos
- Iris_data_manipulation.py: Código que prepara o arquivo Iris para ser utilizado no ID3
3.2) Src/game: Contém todo o código referente ao jogo (AQUI SE JOGA POPOUT):
- board.py: Definição da classe do tabuleiro e suas respectivas funções
- **main.py**: Arquivo main que roda o jogo! Para jogar rode esse arquivo no terminal (python3 main.py) dentro da pasta (src/game)
- mcts.py: Arquivo que define o MCTS base e também suas versões adaptadas com suas respectivas funções e heurísticas
- modos.py: Arquivo que configura os 3 diferentes tipos de jogo
- player.py: Definição da classe e subclasses de jogadores e suas respectivas funções

4) IA_2526_Trab.pdf: Assignment com escopo do trabalho

5) Slide_Apresentaçao.pdf: Pdf contendo slide para apresentação do trabalho