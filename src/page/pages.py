import streamlit as st
import requests


def calcular_imc(peso, altura):
    return round(peso / (altura ** 2), 2)


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
            st.experimental_set_query_params(page="hexad")
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
        st.experimental_set_query_params(page="info")


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
        st.experimental_set_query_params(page="recomendacao")


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
        st.experimental_set_query_params(page="avaliacao")


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
