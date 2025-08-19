import streamlit as st
from src.page.pages import (
    tela_login,
    tela_hexad,
    tela_info_pessoal,
    tela_recomendacao,
    tela_avaliacao,
    tela_cluster
)

def cabecalho_customizado():
    st.markdown("""
        <style>
            .header-bar {
                width: 100%;
                background-color: #0000FF;
                padding: 30px 15px;
                display: flex;
                flex-direction: column;
                align-items: center;
                color: white;
                border-radius: 12px;
                margin-bottom: 5px;
            }

            .header-title {
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
                margin-bottom: 20px; /* Espaço entre título e botões */
            }

            .header-buttons {
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
                justify-content: center;
            }

            .header-buttons form {
                margin: 0;
            }

            .stButton > button {
                border: 1px solid black !important;
                background-color: white !important;
                color: #0000FF !important;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
                height: 3em;
                min-width: 100px;
            }

            .spacer-header {
                height: 10px;
            }
        </style>

        <div class="header-bar">
            <div class="header-title">🧩 Formulário de Gamificação</div>
            <div class="header-buttons">
    """, unsafe_allow_html=True)

    # Os botões precisam estar dentro da <div class="header-buttons">, então usamos st.button normalmente.
    # OBS: Cada st.button gera um <form>, que já está estilizado para não ter margem.
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.button("Login", key="login", on_click=lambda: muda_pagina("login"))
    with col2:
        st.button("Hexad", key="hexad", on_click=lambda: muda_pagina("hexad"))
    with col3:
        st.button("Info", key="info", on_click=lambda: muda_pagina("info"))
    with col4:
        st.button("Output", key="recomendacao", on_click=lambda: muda_pagina("recomendacao"))
    with col5:
        st.button("Avaliação", key="avaliacao", on_click=lambda: muda_pagina("avaliacao"))

    st.markdown("""
            </div>
        </div>
    """, unsafe_allow_html=True)

def muda_pagina(pagina):
    st.session_state.pagina = pagina
    st.query_params["pagina"] = pagina
    st.rerun()

def main():
    # 🔄 Sincroniza o parâmetro da URL com session_state
    query_params = st.query_params  # ou st.experimental_get_query_params() se estiver usando versão antiga
    pagina_url = query_params.get("pagina", [None])[0] if isinstance(query_params.get("pagina"), list) else query_params.get("pagina")


    if pagina_url and pagina_url != st.session_state.get("pagina"):
        st.session_state.pagina = pagina_url


    cabecalho_customizado()

    # Página inicial padrão
    if "pagina" not in st.session_state:
        st.session_state.pagina = "login"

    # Se uma página futura foi definida, navegue para ela
    if "page_to_navigate" in st.session_state:
        st.session_state.pagina = st.session_state.page_to_navigate
        del st.session_state.page_to_navigate
        st.rerun()
        return

    # Dicionário de rotas
    rotas = {
        "login": tela_login,
        "hexad": tela_hexad,
        "info": tela_info_pessoal,
        "recomendacao": tela_recomendacao,
        "avaliacao": tela_avaliacao,
        "cluster": tela_cluster,

    }

    # Executa a tela da página atual
    rotas.get(st.session_state.pagina, tela_login)()

if __name__ == "__main__":
    main()
