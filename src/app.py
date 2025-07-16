import streamlit as st
from page.pages import (
    tela_login,
    tela_hexad,
    tela_info_pessoal,
    tela_recomendacao,
    tela_avaliacao
)

# Leitura da URL
pagina = st.experimental_get_query_params().get("page", ["login"])[0]

# Navegação baseada em parâmetro
rotas = {
    "login": tela_login,
    "hexad": tela_hexad,
    "info": tela_info_pessoal,
    "recomendacao": tela_recomendacao,
    "avaliacao": tela_avaliacao,
}

rotas.get(pagina, tela_login)()
