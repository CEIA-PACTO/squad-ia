# item_tower.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from curatorship import *


class ItemTower:
    def __init__(self, path='../dataframes/desafios.csv'):
        self.df = pd.read_csv(path, sep='\t', encoding='iso-8859-1')
        self.scaler = StandardScaler()
        self.item_embeddings = None
        self.pca = PCA(n_components=5)

    def preprocess(self):
        # Verificar se as colunas necessárias existem no dataframe
        required_columns = ['intensidade', 'tipo', 'descricao']
        missing_columns = [col for col in required_columns if col not in self.df.columns]

        if missing_columns:
            raise KeyError(f"Faltam as colunas necessárias: {', '.join(missing_columns)}")

        # Garantir que as colunas corretas estão sendo usadas
        self.df = self.df.fillna(0)  # Preencher valores NaN com 0

        features_to_use = ['intensidade', 'tipo', 'descricao']

        # Verifique a existência de dados para as colunas específicas
        self.df = self.df.dropna(subset=features_to_use)

        # Normalização dos dados
        scaled = self.scaler.fit_transform(self.df[features_to_use])

        # Ajustar o número de componentes do PCA de acordo com a quantidade de dados
        n_components = min(5, scaled.shape[0], scaled.shape[1])

        # Aplicando PCA
        self.pca = PCA(n_components=n_components)
        self.item_embeddings = self.pca.fit_transform(scaled)

    def get_item_embedding(self, desafio_codigo):
        if self.item_embeddings is None:
            self.preprocess()
        idx = self.df[self.df['desafio_codigo'] == desafio_codigo].index
        return self.item_embeddings[idx[0]] if len(idx) else None

    def get_all_embeddings(self):
        if self.item_embeddings is None:
            self.preprocess()
        return self.df[['desafio_codigo']].assign(embedding=list(self.item_embeddings))
