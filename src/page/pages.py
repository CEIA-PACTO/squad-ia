import requests
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import euclidean_distances
import random

def calcular_imc(peso, altura):
    return round(peso / (altura ** 2), 2)

# ----------------------------------------------------------------------------------------------------------------------

def tela_login():

    st.title("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Avançar"):
        if usuario and senha:
            st.session_state.dados = {
                "usuario": usuario,
                "senha": senha
            }

            st.session_state.page_to_navigate = "hexad"
            st.rerun()
        else:
            st.warning("Preencha usuário e senha.")




def tela_hexad():
    st.title("🎮 Perfil Gamificado - Modelo HEXAD")
    st.markdown("Se você **não sabe** seu perfil, acesse: [HEXAD Quiz](https://www.gamified.uk/user-types/)")

    persona_primaria = st.selectbox("Persona primária", ["conquistador", "jogador", "filantropo", "socializador", "livre", "disruptor"])
    persona_secundaria = st.selectbox("Persona secundária", ["conquistador", "jogador", "filantropo", "socializador", "livre", "disruptor"])
    importancia_amigos = st.slider("Importância dos amigos", 0, 5)
    importancia_resultados = st.slider("Importância dos resultados", 0, 5)
    importancia_diversao = st.slider("Importância da diversão", 0, 5)

    if st.button("Próxima Etapa"):
        st.session_state.dados.update({
            "persona_primaria": persona_primaria,
            "persona_secundaria": persona_secundaria,
            "importancia_amigos": importancia_amigos,
            "importancia_resultados": importancia_resultados,
            "importancia_diversao": importancia_diversao
        })
        st.session_state.page_to_navigate = "info"
        st.rerun()


def tela_info_pessoal():
    st.title("📋 Informações Pessoais")

    sexo = st.radio("Sexo", ["Masculino", "Feminino", "Outro"])
    idade = st.number_input("Idade", min_value=0, max_value=120, step=1)
    altura = st.number_input("Altura (m)", min_value=0.5, max_value=2.5, step=0.01)
    peso = st.number_input("Peso (kg)", min_value=0.0, max_value=300.0, step=0.1)

    hipertensao = st.checkbox("Você tem hipertensão?")
    diabetes = st.checkbox("Você tem diabetes?")

    nivel = st.selectbox("Nível de atividade física", ["Iniciante", "Intermediário", "Avançado"])
    objetivo = st.selectbox("Objetivo", ["Emagrecer", "Ganho de Massa", "Condicionamento", "Outro"])
    tipo_fitness = st.selectbox("Tipo de treino preferido", ["Funcional", "Musculação", "Cardio", "Outro"])

    if st.button("Finalizar"):
        imc = calcular_imc(peso, altura)
        st.session_state.dados.update({
            "Sexo": {"Masculino": 1, "Feminino": 2, "Outro": 3}[sexo],
            "Idade": idade,
            "Altura": altura,
            "Peso": peso,
            "Hipertensao": int(hipertensao),
            "Diabetes": int(diabetes),
            "IMC": imc,
            "Nivel": {"Iniciante": 1, "Intermediário": 2, "Avançado": 3}[nivel],
            "Objetivo": {"Emagrecer": 1, "Ganho de Massa": 2, "Condicionamento": 3, "Outro": 4}[objetivo],
            "Tipo_Fitness": {"Funcional": 0, "Musculação": 1, "Cardio": 2, "Outro": 3}[tipo_fitness]
        })
        st.session_state.page_to_navigate = "recomendacao"
        st.rerun()


def tela_recomendacao():
    st.title("✅ Cadastro Concluído")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Dados Cadastrados")
        st.json(st.session_state.dados)

    with col2:
        st.subheader("🤖 Recomendação Personalizada")
        try:
            response = requests.post(
                "http://localhost:8000/recomendar",
                json=st.session_state.dados
            )
            if response.status_code == 200:
                recomendacao = response.json()
                st.success("Recomendação recebida com sucesso:")
                st.json(recomendacao)
            else:
                st.error(f"Erro {response.status_code} ao obter recomendação.")
                st.text(response.text)
        except Exception as e:
            st.error("Erro ao conectar com o servidor FastAPI.")
            st.text(str(e))

    st.markdown("---")
    st.markdown("### Deseja avaliar a recomendação?")
    if st.button("👉 Avaliar Recomendação"):
        st.session_state.page_to_navigate = "avaliacao"
        st.rerun()


def tela_avaliacao():
    st.title("📝 Avaliação Final")
    st.markdown("Ajude-nos a entender seu progresso e experiência com a recomendação recebida.")

    if "avaliacoes_positivas" not in st.session_state:
        st.session_state.avaliacoes_positivas = 0

    success = st.radio("Você teve sucesso com a recomendação?", ["Sim", "Não"])
    streak = st.number_input("Dias seguidos mantendo a recomendação", min_value=0, step=1)
    progress_pct = st.slider("Porcentagem de progresso percebido (%)", 0, 100)
    rating = st.slider("Nota geral para a recomendação", 1, 5)
    time = st.number_input("Tempo (em minutos) diário dedicado", min_value=0, step=5)

    if st.button("Enviar Avaliação"):
        payload_avaliacao = {
            "usuario": st.session_state.dados["usuario"],
            "senha": st.session_state.dados["senha"],
            "success": success == "Sim",
            "streak": streak,
            "progress_pct": progress_pct,
            "rating": rating,
            "time": time
        }

        if success == "Sim":
            st.session_state.avaliacoes_positivas += 1

        try:
            response = requests.post("http://localhost:8000/avaliar", json=payload_avaliacao)
            if response.status_code == 200:
                resultado = response.json()
                st.success("Avaliação enviada com sucesso!")
                st.json(resultado)
            else:
                st.error(f"Erro {response.status_code} ao enviar avaliação.")
                st.text(response.text)
        except Exception as e:
            st.error("Erro ao conectar com o servidor FastAPI.")
            st.text(str(e))

    st.info(f"Total de avaliações positivas: {st.session_state.avaliacoes_positivas}")
# ----------------------------------------------------------------------------------------------------------------------

def tela_cluster():
    st.title("🔍 Análise de Cluster do Usuário")

    # ========== 1. Dados fixos do cliente ==========
    dados_cliente = {
        "Sexo": 1,
        "Idade": 30,
        "Altura": 1.75,
        "Peso": 75.0,
        "Hipertensao": 0,
        "Diabetes": 0,
        "IMC": 24.5,
        "Nivel": 2,
        "Objetivo": 1,
        "Tipo_Fitness": 0,
        "persona_primaria": "conquistador",
        "persona_secundaria": "jogador",
        "importancia_amigos": 4,
        "importancia_resultados": 5,
        "importancia_diversao": 3,
        "senha": "senhasecreta123",
        "usuario": "admin"
    }

    # ========== 2. Gerar posição do cliente com base nos dados ==========
    X_cliente = (
        dados_cliente["importancia_resultados"] * 10 +
        dados_cliente["IMC"] +
        dados_cliente["Nivel"] * 5
    )

    Y_cliente = (
        dados_cliente["importancia_amigos"] * 10 +
        dados_cliente["importancia_diversao"] * 5 +
        dados_cliente["Idade"] * 0.5
    )

    cliente = pd.DataFrame({'X': [X_cliente], 'Y': [Y_cliente]})

    # ========== 3. Dados simulados dos outros usuários ==========
    np.random.seed(42)
    data = pd.DataFrame({
        'X': np.random.normal(50, 15, 200),
        'Y': np.random.normal(50, 15, 200),
    })

    # ========== 4. Centroides fixos ==========
    centroids = pd.DataFrame({
        'X': [40, 60, 50],
        'Y': [40, 60, 70],
    })

    clusters_hexad = ['Achiever', 'Free Spirit', 'Socializer']
    dists = euclidean_distances(cliente, centroids)[0]
    df_dists = pd.DataFrame({
        'Cluster': clusters_hexad,
        'Distância': dists
    }).sort_values(by="Distância")

    # ========== 5. Layout com dois gráficos ==========
    col1, col2 = st.columns(2)

    # ----- Gráfico 1: Dispersão com cliente e centroides -----
    with col1:
        fig1, ax1 = plt.subplots()
        ax1.scatter(data['X'], data['Y'], alpha=0.4, label='Usuários')
        ax1.scatter(cliente['X'], cliente['Y'], color='red', s=100, label='Cliente')
        ax1.scatter(centroids['X'], centroids['Y'], color='green', marker='X', s=100, label='Centroides')

        for i in range(len(centroids)):
            ax1.plot(
                [cliente['X'][0], centroids['X'][i]],
                [cliente['Y'][0], centroids['Y'][i]],
                linestyle='--', color='gray'
            )
            ax1.text(centroids['X'][i]+1, centroids['Y'][i]+1, f"C{i} ({dists[i]:.2f})")

        ax1.set_title("📍 Posição do Cliente vs Centroides")
        ax1.legend()
        st.pyplot(fig1)

    # ----- Gráfico 2: Histograma de engajamento fictício -----
    with col2:
        data['Engajamento'] = np.random.normal(60, 10, 200)
        engajamento_cliente = 70 if dados_cliente["persona_primaria"] == "conquistador" else 60

        fig2, ax2 = plt.subplots()
        ax2.hist(data['Engajamento'], bins=20, alpha=0.6, label='Usuários')
        ax2.axvline(engajamento_cliente, color='red', linestyle='--', label='Cliente')
        ax2.set_title("🎯 Comparativo de Engajamento")
        ax2.set_xlabel("Engajamento")
        ax2.set_ylabel("Frequência")
        ax2.legend()
        st.pyplot(fig2)

    # ========== 6. Análise textual ==========
    st.subheader("📌 Análise de Proximidade")
    st.markdown(f"""
        O cliente foi comparado com os centroides de 3 perfis de personalidade do modelo **Hexad**.

        **As duas personalidades mais próximas são:**
        1. **{df_dists.iloc[0]['Cluster']}** – distância: `{df_dists.iloc[0]['Distância']:.2f}`
        2. **{df_dists.iloc[1]['Cluster']}** – distância: `{df_dists.iloc[1]['Distância']:.2f}`

        Isso sugere que o usuário tem características mais alinhadas com os perfis acima.
    """)
