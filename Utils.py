import numpy as np


def preencher_nulos_coluna(df, coluna, metodo='bootstrap', seed=None):
    """
    Preenche valores nulos em uma coluna numérica de um DataFrame com dados simulados.

    Parâmetros:
        df (pd.DataFrame): DataFrame de entrada
        coluna (str): Nome da coluna com nulos a ser preenchida
        metodo (str): 'bootstrap' (padrão) ou 'normal'
        seed (int): Semente para reprodutibilidade

    Retorna:
        pd.Series: Coluna com nulos preenchidos
    """
    if seed is not None:
        np.random.seed(seed)

    col = df[coluna]
    n_nulos = col.isna().sum()

    if n_nulos == 0:
        return col  # Nenhum nulo

    valores_validos = col.dropna()

    if metodo == 'bootstrap':
        substitutos = np.random.choice(valores_validos, size=n_nulos, replace=True)
    elif metodo == 'normal':
        media = valores_validos.mean()
        desvio = valores_validos.std()
        substitutos = np.random.normal(loc=media, scale=desvio, size=n_nulos)
    else:
        raise ValueError("Método inválido. Use 'bootstrap' ou 'normal'.")

    col_preenchida = col.copy()
    col_preenchida.loc[col.isna()] = substitutos

    return col_preenchida
