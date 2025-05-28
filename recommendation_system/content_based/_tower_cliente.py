# user_tower.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from curatorship import *


N_COMPONENTS = 5

class UserTower:
    def __init__(self, path='../dataframes/avaliacaofisica.csv'):
        self.df = pd.read_csv(path, sep='\t', encoding='iso-8859-1')
        self.scaler = StandardScaler()
        self.user_embeddings = None
        self.pca = PCA(n_components=N_COMPONENTS)

    def preprocess(self):

        self.df['nivel_fisico'] = self.df['abdominal'].apply(classificar_abdominais)
        self.df['faixa_imc'] = self.df['imc'].apply(classificar_imc)

        self.df['persona'] = self.df.apply(atribuir_persona, axis=1)
        self.df = self.df.fillna(0)

        features_to_use = [
            'peso', 'altura', 'imc', 'massamagra', 'massagorda',
            'percentualgordura', 'gorduravisceral', 'tmb'
        ]
        # Garante que os dados existam
        self.df = self.df.dropna(subset=features_to_use + ['persona'])
        self.df = self.df[features_to_use + ['cliente_codigo', 'persona']]

        # Normalização
        scaled = self.scaler.fit_transform(self.df[features_to_use])

        # Ajuste o número de componentes conforme o mínimo entre samples e features
        n_components = min(N_COMPONENTS, scaled.shape[0], scaled.shape[1])

        # Aplicar PCA
        self.pca = PCA(n_components=n_components)
        self.user_embeddings = self.pca.fit_transform(scaled)

    def get_user_embedding(self, cliente_codigo):
        if self.user_embeddings is None:
            self.preprocess()
        idx = self.df[self.df['cliente_codigo'] == cliente_codigo].index
        return self.user_embeddings[idx[0]] if len(idx) else None

    def get_all_embeddings(self):
        if self.user_embeddings is None:
            self.preprocess()
        return self.df[['cliente_codigo', 'persona']].assign(embedding=list(self.user_embeddings))
