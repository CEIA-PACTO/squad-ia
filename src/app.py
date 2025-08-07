import streamlit as st
from page.pages import (tela_login,
                        tela_hexad,
                        tela_info_pessoal,
                        tela_recomendacao,
                        tela_avaliacao)

pagina = st.query_params.get("page", "login")

rotas = {
    "login": tela_login,
    "hexad": tela_hexad,
    "info": tela_info_pessoal,
    "recomendacao": tela_recomendacao,
    "avaliacao": tela_avaliacao,
}

rotas.get(pagina, tela_login)()
