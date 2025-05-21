import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from scipy.stats import zscore
from Utils import preencher_nulos_coluna
from sklearn.preprocessing import LabelEncoder

class AvaliacaoFisica:

    def __init__(self, filepath: str = "../dataframes/avaliacaofisica.csv"):
        self.data = pd.read_csv(filepath, sep='\t', encoding='iso-8859-1')
        self.id_cols = ['_chave', 'cliente_codigo']

    def _null_features(self, data: pd.DataFrame):
        colunas_para_remover = [
            'aumentopercentualgordura', 'vomaxaerobico', 'venda', 'recomendacoes', 'urlassinatura',
            'agendamentoreavaliacao_codigo', 'assinatura', 'codigo', 'dataavaliacao', 'tempo2400', 'pesoosseo',
            'resistencia', 'dataproxima', 'endomorfia', 'fcastrand', 'fcastrand4', 'fcastrand5', 'reatancia',
            'necessidadefisica', 'necessidadecalorica', 'gorduraideal', 'logbalanca', 'massamagra', 'mesomorfia',
            'metapercentualgordura', 'metapercentualgorduraanterior', 'movproduto'
        ]
        data.drop(columns=colunas_para_remover, inplace=True, errors='ignore')

        def preencher_cruzado(df, col1, col2):
            cond1 = df[col1].isnull() & df[col2].notnull()
            cond2 = df[col2].isnull() & df[col1].notnull()
            df.loc[cond1, col1] = df.loc[cond1, col2]
            df.loc[cond2, col2] = df.loc[cond2, col1]

        preencher_cruzado(data, 'antebracoesq', 'antebracodir')
        preencher_cruzado(data, 'bracocontraidodir', 'bracocontraidoesq')
        preencher_cruzado(data, 'bracorelaxadoesq', 'bracorelaxadodir')
        preencher_cruzado(data, 'coxaproximaldir', 'coxaproximalesq')

        data.fillna(-1, inplace=True)  # <-- agora é efetivo
        return data


    def _duplicates_features(self, data):
        return data.drop_duplicates(ignore_index=True)


    def _encode_features(self, data):
        cat_cols = data.select_dtypes(include=['object', 'category']).columns.difference(self.id_cols)
        return pd.get_dummies(data, columns=cat_cols, drop_first=True)


    def _remove_outliers(self, data, z_thresh=3, max_outlier_ratio=0.5):
        data_copy = data.copy()
        numeric = data_copy.drop(columns=self.id_cols, errors='ignore').select_dtypes(include=['float64', 'int64'])
        z_scores = zscore(numeric)
        z_scores_df = pd.DataFrame(z_scores, columns=numeric.columns, index=numeric.index)
        outlier_mask = (abs(z_scores_df) > z_thresh)
        outlier_counts = outlier_mask.sum(axis=1)
        max_outliers = int(max_outlier_ratio * numeric.shape[1])
        keep_rows = outlier_counts <= max_outliers
        return data_copy[keep_rows]


    def _scale_features(self, data):
        if data.empty:
            raise ValueError("Nenhuma feature disponível para escalonamento.")
        scaler = StandardScaler()
        scaled = pd.DataFrame(scaler.fit_transform(data), columns=data.columns, index=data.index)
        return scaled


    def _feature_selection(self, data, threshold=0.01):
        numeric = data.select_dtypes(include=['float64', 'int64'])
        selected = numeric.loc[:, numeric.var() > threshold]
        return selected

    def main(self):
        data = self.data.copy()
        data = self._null_features(data)
        data = self._duplicates_features(data)
        data = self._encode_features(data)
        data = self._remove_outliers(data)  # <- aplicar aqui antes de isolar features

        ids = data[self.id_cols].reset_index(drop=True)
        features = data.drop(columns=self.id_cols)
        features = self._feature_selection(features)
        features_scaled = self._scale_features(features)

        return ids, features_scaled

class TreinoRealizado:

    def __init__(self, file_path : dict = {'programa_treino' : '../dataframes/programatreino.csv','treino_realizado': '../dataframes/treinorealizado.csv','cliente' : '../dataframes/cliente.csv'}):
        self.treino = pd.read_csv(file_path['treino_realizado'], sep='\t', encoding='iso-8859-1')
        self.cliente = pd.read_csv(file_path['cliente'], sep=',', encoding='iso-8859-1')
        self.programa = pd.read_csv(file_path['programa_treino'], sep='\t', encoding='iso-8859-1')
        self.ids = ['_chave', 'matricula', 'cliente_codigo', 'professor_codigo', 'programatreinoficha_codigo', 'empresa', 'nome']

    def _null_features(self):
        # Limpeza treino
        self.treino.drop(columns=[
            'chaveexecucao', 'comentario', 'datafim',
            'professoracompanhamento_codigo', 'unidadeexecucao'
        ], inplace=True, errors='ignore')

        self.treino = self.treino.dropna(subset=['cliente_codigo'])
        self.treino['nota'] = preencher_nulos_coluna(self.treino, 'nota')
        self.treino['tempoutil'] = preencher_nulos_coluna(self.treino, 'tempoutil')

        # Limpeza programa
        self.programa.drop(columns=[
            'codigocolaborador', 'datalancamento', 'datarenovacao',
            'emrevisaoprofessor', 'dataultimaatualizacao', 'genero',
            'idoperacaoemmassa', 'nivel_codigo', 'isgeradoporia', 'dataterminoprevisto'
            'predefinido', 'professormontou_codigo', 'professorcarteira_codigo',
            'treinorapido', 'programatreinorenovado', 'programatreinorenovacao'
        ], inplace=True, errors='ignore')

        self.programa = self.programa.dropna(subset=['cliente_codigo'])
        self.programa['diasporsemana'] = preencher_nulos_coluna(self.programa, 'diasporsemana')
        self.programa['nrtreinosrealizados'] = preencher_nulos_coluna(self.programa, 'nrtreinosrealizados')
        self.programa['totalaulasprevistas'] = preencher_nulos_coluna(self.programa, 'totalaulasprevistas')

        self.cliente.drop(columns=[
            'datainclusaospc', 'categoria', 'idexterno',
            'matriculaexterna', 'objecao', 'pessoaresponsavel',
            'responsavelfreepass', 'gympasstypenumber', 'parqpositivo',
            'renda', 'sincronizadoredeempresa', 'uacodigo'
        ], inplace=True, errors='ignore')

        self.cliente = self.cliente.dropna(subset=['codigo'])
        self.cliente['titularplanocompartilhado'] = self.cliente['titularplanocompartilhado'].notnull()
        self.cliente['indicadopor'] = self.cliente['indicadopor'].notnull()
        self.cliente['freepass'] = self.cliente['freepass'].notnull()

    def _merge(self):
        # Primeira junção: treino (t) + cliente (c)
        merged_df = pd.merge(
            self.treino,
            self.cliente,
            left_on=['cliente_codigo', '_chave'],
            right_on=['codigo', '_chave'],
            how='left',
            suffixes=('', '_cliente')
        )

        # Remove a coluna 'codigo' do cliente (já temos cliente_codigo do treino)
        if 'codigo' in merged_df.columns:
            merged_df.drop(columns=['codigo'], inplace=True)

        # Segunda junção: resultado anterior + programa (p)
        merged_df = pd.merge(
            merged_df,
            self.programa,
            left_on=['cliente_codigo', '_chave'],
            right_on=['cliente_codigo', '_chave'],
            how='inner',
            suffixes=('', '_programa')
        )

        # Remover campo 'chave' de self.programa para evitar redundância
        if 'chave' in merged_df.columns:
            merged_df.drop(columns=['chave'], inplace=True)


        merged_df
        return merged_df

    def _duplicates(self):
        self.data.drop_duplicates(inplace=True)

    def _features(self):
        data_atual = pd.Timestamp.today()

        self.data['datainicio'] = pd.to_datetime(self.data['datainicio'], errors='coerce')
        self.data['tempo_total'] = ((data_atual.year - self.data['datainicio'].dt.year) * 12 +(data_atual.month - self.data['datainicio'].dt.month))
        self.data.drop(columns=['datainicio'], inplace=True)

        self.data['datainicio_programa'] = pd.to_datetime(self.data['datainicio_programa'], errors='coerce')
        self.data['tempo_programa'] = ((data_atual.year - self.data['datainicio_programa'].dt.year) * 12 + (data_atual.month - self.data['datainicio_programa'].dt.month))
        self.data.drop(columns=['datainicio_programa'], inplace=True)

        self.data['dataproximarevisao'] = pd.to_datetime(self.data['dataproximarevisao'], errors='coerce')
        self.data['tempo_proxima_revisao'] = ((self.data['dataproximarevisao'].dt.year - data_atual.year) * 12 +(self.data['dataproximarevisao'].dt.month - data_atual.month))
        self.data.drop(columns=['dataproximarevisao'], inplace=True)

    def _encouder(self):
        cols_para_codificar = [
            'executadofichadia',
            'freepass',
            'indicadopor',
            'titularplanocompartilhado',
            'situacao'
        ]

        for col in cols_para_codificar:
            if col in self.data.columns:
                le = LabelEncoder()
                # Converte para string para evitar erros com tipos mistos (bool, NaN etc.)
                self.data[col] = le.fit_transform(self.data[col].astype(str))

    def main(self):
        self._null_features()

        self.data = self._merge()

        self._duplicates()
        self._features()
        self._encouder()

        ids = self.data[self.ids]
        data = self.data.drop(self.ids, axis=1)
        return ids, data

if __name__ == '__main__':
    av_ids, avaliacao_fisica = AvaliacaoFisica().main()
    print(avaliacao_fisica)
    a, b = TreinoRealizado().main()
    print(b)
