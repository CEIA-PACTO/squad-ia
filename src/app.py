import streamlit as st
from page.pages import (
    aplicar_estilo,
    cabecalho_customizado,
    tela_login,
    tela_hexad,
    tela_info_pessoal,
    tela_recomendacao,
    tela_avaliacao
)

def main():
    aplicar_estilo()
    cabecalho_customizado()

    if "page_to_navigate" in st.session_state:
        st.query_params["page"] = st.session_state.page_to_navigate
        del st.session_state.page_to_navigate  # Limpa para não repetir sempre
        st.rerun()
        return

    pagina = st.query_params.get("page", ["login"])[0]

    rotas = {
        "login": tela_login,
        "hexad": tela_hexad,
        "info": tela_info_pessoal,
        "recomendacao": tela_recomendacao,
        "avaliacao": tela_avaliacao,
    }

    rotas.get(pagina, tela_login)()

if __name__ == "__main__":
    main()
