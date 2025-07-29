import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.neighbors import NearestNeighbors
from collections import Counter
from typing import List, Union, Dict, Any
import random
import os
import json


class RecomendadorCF:
    def __init__(
        self,
        path_excel: str = "dataframe/gym_recommendation.xlsx",
        exerc_col: str = "Exercises",
        exercises_sep: str = ",",
        n_neighbors: int = 50,
        metric: str = "cosine",
    ):

        caminho_atual = os.getcwd()
        print("Caminho atual:", caminho_atual)

        self.path_excel = path_excel
        self.exerc_col = exerc_col
        self.exercises_sep = exercises_sep
        self.n_neighbors = n_neighbors
        self.metric = metric

        # Carrega e limpa o BD
        self.df_raw = pd.read_excel(self.path_excel)
        # Ajuste nomes para um padrão (opcional)
        self.df_raw = self._rename_columns(self.df_raw)

        # Guarda colunas
        self.num_cols = ["Age", "Height", "Weight", "BMI"]
        self.cat_cols = [
            "Sex",
            "Hypertension",
            "Diabetes",
            "Level",
            "Fitness Goal",
            "Fitness Type",
        ]

        # Remover colunas que não serão usadas (se existirem)
        drop_cols = ["Diet", "ID", "Recommendation"]
        self.df_raw = self.df_raw.drop(columns=[c for c in drop_cols if c in self.df_raw.columns])

        # Separa X (atributos) e y (exercícios)
        self.X = self.df_raw[self.num_cols + self.cat_cols].copy()
        self.y_exercises = self.df_raw[self.exerc_col].fillna("").astype(str)

        # Pipeline de pré-processamento
        self.preprocess = self._build_preprocess_pipeline()

        # Ajusta pipeline e KNN
        self._fit()

    def recomendar(
        self,
        registro: Union[Dict[str, Any], pd.Series, pd.DataFrame],
        top_n: int = 5,
        excluir_existentes: bool = True,
    ) -> List[str]:
        """
        Gera recomendação de exercícios para um único registro.

        registro: dicionário/Series/DataFrame com as mesmas chaves/colunas do BD.
        top_n: quantos exercícios retornar.
        excluir_existentes: remove do ranking exercícios já praticados pelo usuário (se fornecido no registro).
        """
        registro_df = self._coerce_to_dataframe(registro)
        registro_df = self._rename_columns(registro_df)

        # Garante que todas as colunas estão presentes
        missing_cols = set(self.num_cols + self.cat_cols) - set(registro_df.columns)
        if missing_cols:
            raise ValueError(f"Faltam colunas no registro de entrada: {missing_cols}")

        x_vec = self.preprocess.transform(registro_df[self.num_cols + self.cat_cols])

        distances, indices = self.knn_model.kneighbors(x_vec, n_neighbors=self.n_neighbors)
        neighbor_idx = indices[0]
        exercises_list = []
        for idx in neighbor_idx:
            exercises_list.extend(self._split_exercises(self.y_exercises.iloc[idx]))

        # Remove exercícios já existentes, se houver
        if excluir_existentes and (self.exerc_col in registro_df.columns):
            user_ex = self._split_exercises(str(registro_df[self.exerc_col].iloc[0]))
            exercises_list = [e for e in exercises_list if e not in user_ex]

        # Rank por frequência
        counts = Counter([e.strip() for e in exercises_list if e.strip()])
        recomendados = [ex for ex, _ in counts.most_common(top_n)]
        return recomendados

    # ------------------------------------------------------------------
    # Métodos internos auxiliares
    # ------------------------------------------------------------------
    def _fit(self):
        X_proc = self.preprocess.fit_transform(self.X)
        self.knn_model = NearestNeighbors(metric=self.metric, n_neighbors=self.n_neighbors)
        self.knn_model.fit(X_proc)

    def _build_preprocess_pipeline(self) -> ColumnTransformer:
        """Cria o pipeline de pré-processamento, compatível com diferentes versões do
        scikit-learn (mudança do parâmetro `sparse` -> `sparse_output` a partir da 1.2).
        """
        num_pipe = StandardScaler()
        # Compatibilidade de versões
        try:
            cat_pipe = OneHotEncoder(handle_unknown="ignore", sparse_output=True)
        except TypeError:
            # Para versões antigas (<1.2)
            cat_pipe = OneHotEncoder(handle_unknown="ignore", sparse=True)

        return ColumnTransformer(
            transformers=[
                ("num", num_pipe, self.num_cols),
                ("cat", cat_pipe, self.cat_cols),
            ]
        )

    def _split_exercises(self, cell: str) -> List[str]:
        if not isinstance(cell, str):
            return []
        return [c.strip() for c in cell.split(self.exercises_sep) if c.strip()]

    @staticmethod
    def _coerce_to_dataframe(registro: Union[Dict[str, Any], pd.Series, pd.DataFrame]) -> pd.DataFrame:
        if isinstance(registro, pd.DataFrame):
            return registro.copy()
        if isinstance(registro, pd.Series):
            return registro.to_frame().T
        if isinstance(registro, dict):
            return pd.DataFrame([registro])
        raise TypeError("registro deve ser dict, Series ou DataFrame")

    @staticmethod
    def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza alguns nomes que podem vir em PT-BR no seu código original
        para os nomes das colunas do BD informado no enunciado.
        Ajuste aqui se precisar mapear outros nomes.
        """
        mapping = {
            # PT -> EN
            "Sexo": "Sex",
            "Hipertensao": "Hypertension",
            "Hipertensão": "Hypertension",
            "Diabetes": "Diabetes",
            "Nivel": "Level",
            "Nível": "Level",
            "Objetivo": "Fitness Goal",
            "Tipo_Fitness": "Fitness Type",
            "Tipo Fitness": "Fitness Type",
            "Exercicios": "Exercises",
            "Exercícios": "Exercises",
            "Equipamento": "Equipment",
            "Recomendacao": "Recommendation",
            "Recomendação": "Recommendation",
            "Idade": "Age",
            "Altura": "Height",
            "Peso": "Weight",
            "IMC": "BMI",
        }
        cols = {c: mapping.get(c, c) for c in df.columns}
        return df.rename(columns=cols)


# -----------------------------
# Extensão: híbrido CF + Conteúdo baseado no histórico do usuário
# -----------------------------
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


class RecomendadorPersonalizado(RecomendadorCF):

    def __init__(
        self,
        path_excel: str = "../dataframe/gym_recommendation.xlsx",
        path_hist_csv: str = "../../bd/registro_recomendacoes.csv",
        id_col_hist: str = "id",
        min_hist_rows: int = 5,
        **kwargs,
    ):
        super().__init__(path_excel=path_excel, **kwargs)
        self.path_hist_csv = path_hist_csv
        self.id_col_hist = id_col_hist
        self.min_hist_rows = min_hist_rows

        # Carrega histórico se existir
        try:
            self.hist_df = pd.read_csv(self.path_hist_csv)
        except FileNotFoundError:
            self.hist_df = pd.DataFrame()

        # Vetorização TF-IDF do campo de exercícios do BD base (conteúdo)
        self.tfidf = TfidfVectorizer(token_pattern=r"[A-Za-zÀ-ÖØ-öø-ÿ]+", lowercase=True)
        self.tfidf_matrix = self.tfidf.fit_transform(self.df_raw[self.exerc_col].fillna(""))

    def recomendar_para_usuario(
        self,
        user_id: str,
        registro: Union[Dict[str, Any], pd.Series, pd.DataFrame],
        top_n: int = 5,
        excluir_existentes: bool = True,
    ) -> List[str]:
        """
        Recomendação híbrida.
        - Se o usuário tem histórico >= min_hist_rows: usa CB (conteúdo) com base no texto "Recomendacao_Exercicio" do histórico.
        - Caso contrário: usa CF padrão (herdado).
        """
        if self._tem_historico(user_id):
            return self._recomendar_conteudo(user_id, top_n=top_n)
        else:
            # CF normal herdado
            recs = self.recomendar(registro, top_n=top_n, excluir_existentes=excluir_existentes)
            return recs

    # ---------------- Privados ----------------
    def _tem_historico(self, user_id: str) -> bool:
        if self.hist_df.empty:
            return False
        return (self.hist_df[self.id_col_hist] == user_id).sum() >= self.min_hist_rows

    def _recomendar_conteudo(self, user_id: str, top_n: int = 5) -> List[str]:
        # Junta todas as recomendações textuais do usuário para formar o perfil
        user_hist = self.hist_df[self.hist_df[self.id_col_hist] == user_id]
        texto_user = " ".join(user_hist.get("Recomendacao_Exercicio", "").astype(str).tolist())
        if not texto_user.strip():
            # fallback para CF se o texto estiver vazio
            return []

        user_vec = self.tfidf.transform([texto_user])
        # Similaridade com todos os exercícios do BD base
        cosine_sim = linear_kernel(user_vec, self.tfidf_matrix).flatten()
        top_idx = cosine_sim.argsort()[::-1]

        # Monta ranking único
        recomendados = []
        for idx in top_idx:
            exs = self._split_exercises(self.df_raw.iloc[idx][self.exerc_col])
            for e in exs:
                if e not in recomendados:
                    recomendados.append(e)
            if len(recomendados) >= top_n:
                break
        return recomendados[:top_n]

def executar_recomendacao(
    user_id: str,
    payload: Union[Dict[str, Any], pd.Series, pd.DataFrame, str],
    path_excel: str = "src/dataframe/gym_recommendation.xlsx",
    path_hist_csv: str = "../../bd/registro_recomendacoes.csv",
    path_challenger: str = "../dataframe/challenger.json",
    random_rate: float = 0.4,
    n_neighbors: int = 50,
    top_n: int = 5,
) -> Dict[str, Any]:

    # ---------------- Parse payload ----------------
    if isinstance(payload, str):
        payload_dict = json.loads(payload)
    elif isinstance(payload, (dict, pd.Series)):
        payload_dict = dict(payload)
    elif isinstance(payload, pd.DataFrame):
        payload_dict = payload.iloc[0].to_dict()
    else:
        raise TypeError("payload deve ser str (json), dict, Series ou DataFrame")

    # Garante que persona_primaria está presente para o modo aleatório
    persona_primaria = payload_dict.get("persona_primaria")

    # Decide aleatório vs modelo
    usar_random = random.random() < random_rate and persona_primaria is not None

    rec_model = RecomendadorPersonalizado(
        path_excel=path_excel,
        path_hist_csv=path_hist_csv,
        n_neighbors=n_neighbors,
    )


    registro_model = rec_model._rename_columns(pd.DataFrame([payload_dict]))

    # ---------------- Execução ----------------
    if usar_random:
        # carrega challenger
        with open(path_challenger, "r", encoding="utf-8") as f:
            challenger = json.load(f)
        # filtra por type == persona_primaria
        candidatos = [c for c in challenger if str(c.get("type")) == str(persona_primaria)]
        if not candidatos:
            # fallback para qualquer um
            candidatos = challenger
        escolha = random.choice(candidatos)
        rec_exercicio = escolha.get("exercise", "")
        rec_equip = escolha.get("equipment", "")
        fixa = True
    else:
        # Modelo
        recs = rec_model.recomendar_para_usuario(user_id=user_id, registro=registro_model, top_n=top_n)
        rec_exercicio = ", ".join(recs)
        rec_equip = ""
        fixa = False


    now_iso = pd.Timestamp.now().isoformat()
    linha = {
        "id": user_id,
        "Data_Hora": now_iso,
        "usuario": payload_dict.get("usuario", ""),
        "Recomendacao_Exercicio": rec_exercicio,
        "Recomendacao_Equipamento": rec_equip,
        "Recomendacao_Fixa_Usada": fixa,
    }

    linha.update(payload_dict)

    # Garante que CSV exista ou cria
    if not os.path.exists(path_hist_csv):
        pd.DataFrame([linha]).to_csv(path_hist_csv, index=False)
    else:
        # Garantir todas as colunas existentes + novas
        df_old = pd.read_csv(path_hist_csv)
        df_new = pd.DataFrame([linha])
        df_all = pd.concat([df_old, df_new], ignore_index=True)
        df_all.to_csv(path_hist_csv, index=False)

    return linha


# -----------------------------
# Exemplo de uso
# -----------------------------
if __name__ == "__main__":
    rec = RecomendadorPersonalizado(
        path_excel="../dataframe/gym_recommendation.xlsx",
        path_hist_csv="../../bd/registro_recomendacoes.csv",
        n_neighbors=50,
    )

    usuario_id = "df7fb2364f6f7843421fa91c8d3860b71ee65182a2967c127b8a6291654ea8c9"

    novo_usuario = {
        "Sex": "Male",
        "Age": 30,
        "Height": 1.75,
        "Weight": 75,
        "BMI": 24.5,
        "Hypertension": "No",
        "Diabetes": "No",
        "Level": "Intermediate",
        "Fitness Goal": "Lose Weight",
        "Fitness Type": "Cardio",
        "Exercises": "",
    }

    recs = rec.recomendar_para_usuario(user_id=usuario_id, registro=novo_usuario, top_n=5)
    print("Recomendações:", recs)
