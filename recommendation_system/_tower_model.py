from sklearn.preprocessing import LabelEncoder
import pandas as pd
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from curatorship import *

class ItemTower:
    def __init__(self, path='../dataframes/desafios.csv'):
        self.df = pd.read_csv(path)
        self.scaler = StandardScaler()
        self.item_embeddings = None
        self.pca = PCA(n_components=5)

    def preprocess(self):
        # Verificar se as colunas necessárias existem no dataframe
        required_columns = ['intensidade', 'tipo', 'descricao']
        missing_columns = [col for col in required_columns if col not in self.df.columns]

        if missing_columns:
            raise KeyError(f"Faltam as colunas necessárias: {', '.join(missing_columns)}")

        # Preencher valores ausentes com 0
        self.df = self.df.fillna(0)

        features_to_use = ['intensidade', 'tipo']

        # Remover linhas com valores nulos nas colunas importantes
        self.df = self.df.dropna(subset=features_to_use)

        # Codificar as colunas categóricas
        label_encoder = LabelEncoder()
        self.df['intensidade'] = label_encoder.fit_transform(self.df['intensidade'])
        self.df['tipo'] = label_encoder.fit_transform(self.df['tipo'])

        # Normalizar
        scaled = self.scaler.fit_transform(self.df[features_to_use])

        # PCA
        n_components = min(5, scaled.shape[0], scaled.shape[1])
        self.pca = PCA(n_components=n_components)
        self.item_embeddings = self.pca.fit_transform(scaled)

        # ✅ Adicione aqui o desafio_codigo
        self.df['desafio_codigo'] = self.df.index

    def get_item_embedding(self, desafio_codigo):

        if self.item_embeddings is None:
            self.preprocess()
        idx = self.df[self.df['desafio_codigo'] == desafio_codigo].index
        return self.item_embeddings[idx[0]] if len(idx) else None

    def get_all_embeddings(self):
        if self.item_embeddings is None:
            self.preprocess()
        return self.df[['desafio_codigo']].assign(embedding=list(self.item_embeddings))
