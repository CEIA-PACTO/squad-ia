import pickle
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from prompt_toolkit.shortcuts import radiolist_dialog
import pandas as pd
import numpy as np
import joblib
from sklearn.impute import SimpleImputer
from sklearn.base import BaseEstimator
from gamefication_features import TreinoRealizado, AvaliacaoFisica
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

class KMeansGamification:

    def __init__(self, df_features: pd.DataFrame, df_keys: pd.DataFrame):
        self.df_features = df_features.select_dtypes(include=["number"])
        self.df_features = self.df_features.fillna(0)
        self.df_keys = df_keys
        self.kmeans_model = None
        self.kmeans_6_clusters = None

        print(df_features.info())

    def classify_from_pkl(self, new_df: pd.DataFrame, model_path: str) -> pd.DataFrame:

        new_df = new_df.fillna(0)
        model = joblib.load(model_path)

        if not hasattr(model, "transform"):
            raise ValueError("O modelo carregado não é um KMeans válido ou não possui o método 'transform'.")

        if hasattr(model, 'feature_names_in_'):
            required_columns = list(model.feature_names_in_)
        else:
            raise ValueError("O modelo não contém 'feature_names_in_'. Treine com scikit-learn >= 1.0.")

        # Verifica se todas as colunas necessárias estão no DataFrame
        missing_cols = [col for col in required_columns if col not in new_df.columns]
        if missing_cols:
            raise ValueError(f"Colunas ausentes no DataFrame: {missing_cols}")

        data = new_df[required_columns]

        # Imputação apenas nas colunas numéricas que têm pelo menos um valor não-nulo
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols_with_values = [col for col in numeric_cols if data[col].notna().any()]

        # Imputar apenas nas colunas válidas
        imputer = SimpleImputer(strategy='mean')
        imputed_data = imputer.fit_transform(data[numeric_cols_with_values])
        data_imputed = pd.DataFrame(imputed_data, columns=numeric_cols_with_values, index=data.index)

        # Substitui as colunas imputadas no DataFrame original
        data.loc[:, numeric_cols_with_values] = data_imputed

        # Agora os dados estão prontos
        distances = model.transform(data)
        primary_class = np.argmin(distances, axis=1)
        secondary_class = np.argsort(distances, axis=1)[:, 1]

        result_df = new_df.copy()
        result_df["classe_primaria"] = primary_class
        result_df["classe_secundaria"] = secondary_class

        return result_df

    def plot_elbow_curve(self, max_k=10):
        if self.df_features.empty:
            raise ValueError("O DataFrame de features está vazio. Verifique os dados de entrada.")

        inertias = []
        K = range(1, max_k + 1)
        for k in K:
            model = KMeans(n_clusters=k, random_state=42)
            model.fit(self.df_features)
            inertias.append(model.inertia_)

        plt.figure(figsize=(8, 5))
        sns.lineplot(x=K, y=inertias, marker='o')
        plt.title("Método do Cotovelo")
        plt.xlabel("Número de Clusters")
        plt.ylabel("Inércia")
        plt.xticks(K)
        plt.grid(True)
        plt.show()

    def train_best_kmeans(self, n_clusters):
        self.kmeans_model = KMeans(n_clusters=n_clusters, random_state=42)
        self.kmeans_model.fit(self.df_features)
        return self.kmeans_model

    def train_kmeans_six_clusters(self):
        self.kmeans_6_clusters = KMeans(n_clusters=6, random_state=42)
        self.kmeans_6_clusters.fit(self.df_features)
        clusters_df = self.df_keys.copy()
        clusters_df['cluster'] = self.kmeans_6_clusters.labels_
        self.clustered_data = clusters_df
        return self.kmeans_6_clusters

    def save_model(self, filename="kmeans_6_clusters.pkl"):
        if self.kmeans_6_clusters:
            with open(filename, 'wb') as f:
                pickle.dump(self.kmeans_6_clusters, f)
        else:
            raise ValueError("Modelo de 6 clusters ainda não foi treinado.")

    def get_model_metrics(self, model=None):
        if model is None:
            if self.kmeans_model:
                model = self.kmeans_model
            elif self.kmeans_6_clusters:
                model = self.kmeans_6_clusters
            else:
                raise ValueError("Nenhum modelo foi treinado ainda.")

        labels = model.predict(self.df_features)
        metrics = {
            "inertia": model.inertia_,
            "silhouette_score": silhouette_score(self.df_features, labels),
            "calinski_harabasz_score": calinski_harabasz_score(self.df_features, labels),
            "davies_bouldin_score": davies_bouldin_score(self.df_features, labels)
        }
        return pd.DataFrame([metrics])


def train_avaliacao_fisica():
    av_ids, avaliacao = AvaliacaoFisica().main()
    print(avaliacao)
    pipe_1 = KMeansGamification(df_features=avaliacao, df_keys=av_ids)
    pipe_1.plot_elbow_curve()
    pipe_1.train_best_kmeans(n_clusters=10)
    pipe_1.train_kmeans_six_clusters()
    pipe_1.save_model("../models/av_modelo_hexad.pkl")
    print(pipe_1.get_model_metrics())


def train_treino_realizado():
    tr_ids, treino = TreinoRealizado().main()
    print(treino)
    pipe_2 = KMeansGamification(df_features=treino, df_keys=tr_ids)
    pipe_2.plot_elbow_curve()
    pipe_2.train_best_kmeans(n_clusters=10)
    pipe_2.train_kmeans_six_clusters()
    pipe_2.save_model("../models/tr_modelo_hexad.pkl")
    print(pipe_2.get_model_metrics())


def test_classification(model = 'av'):
    # Exemplo de uso da classificação
    if model == 'av':
        ids, temp = AvaliacaoFisica().main()
        mode = '../models/av_modelo_hexad.pkl'
    if model == 'treino':
        ids, temp = TreinoRealizado().main()
        mode = '../models/tr_modelo_hexad.pkl'

    pipe = KMeansGamification(df_features=temp, df_keys=ids)
    resultado = pipe.classify_from_pkl(temp, mode)

    print(resultado[["classe_primaria", "classe_secundaria"]].head())


if __name__ == "__main__":
    # train_treino_realizado()
    # train_avaliacao_fisica()
    test_classification(model='treino')
    test_classification(model='av')
