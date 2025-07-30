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
<<<<<<< HEAD
            st.experimental_set_query_params(page="hexad")
=======
            st.query_params["page"] = "hexad"
>>>>>>> d898103 (feat: integrate amnesia dataset with HEXAD-based challenge recommendations)
        else:
            st.warning("Preencha usuário e senha.")


def tela_hexad():
    st.title("🎮 Perfil Gamificado - Modelo HEXAD")
    st.markdown("Se você **não sabe** seu perfil, acesse: [HEXAD Quiz](https://www.gamified.uk/user-types/)")
    st.markdown("**Para cada tipo de jogador, indique seu nível de concordância (0-7):**")

    col1, col2 = st.columns(2)
    
    with col1:
        score_philanthropist = st.slider("Filantropo - Gosto de ajudar outros", 0, 7, 3)
        score_socialiser = st.slider("Socializador - Gosto de interagir socialmente", 0, 7, 3)
        score_free_spirit = st.slider("Livre Espírito - Gosto de liberdade e criatividade", 0, 7, 3)
    
    with col2:
        score_achiever = st.slider("Conquistador - Gosto de progresso e conquistas", 0, 7, 3)
        score_player = st.slider("Jogador - Gosto de recompensas e pontos", 0, 7, 3)
        score_disruptor = st.slider("Disruptor - Gosto de causar mudanças", 0, 7, 3)

    if st.button("Próxima Etapa"):
        st.session_state.dados.update({
            "score_philanthropist": score_philanthropist,
            "score_socialiser": score_socialiser,
            "score_free_spirit": score_free_spirit,
            "score_achiever": score_achiever,
            "score_player": score_player,
            "score_disruptor": score_disruptor
        })
<<<<<<< HEAD
        st.experimental_set_query_params(page="info")
=======
        st.query_params["page"] = "info"
>>>>>>> d898103 (feat: integrate amnesia dataset with HEXAD-based challenge recommendations)


def tela_info_pessoal():
    st.title("📋 Informações Pessoais e Fitness")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Dados Demográficos")
        age = st.number_input("Idade", min_value=16, max_value=80, step=1)
        height = st.number_input("Altura (cm)", min_value=100, max_value=250, step=1)
        weight = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, step=0.5)
        body_type = st.selectbox("Sexo", ["Masculino", "Feminino"])
    
    with col2:
        st.subheader("🏃‍♂️ Dados de Fitness")
        goal = st.selectbox("Objetivo principal", ["Emagrecimento", "Hipertrofia", "Força"])
        training_days = st.number_input("Dias de treino por semana", min_value=1, max_value=7, step=1)
        training_time = st.number_input("Tempo de treino (minutos)", min_value=15, max_value=180, step=15)
        experience_level = st.selectbox("Nível de experiência", ["Iniciante", "Intermediário", "Avançado"])

    if st.button("Finalizar"):
        st.session_state.dados.update({
            "age": age,
            "height": height,
            "weight": weight,
            "body_type": body_type,
            "goal": goal,
            "training_days": training_days,
            "training_time": training_time,
            "experience_level": experience_level
        })
<<<<<<< HEAD
        st.experimental_set_query_params(page="recomendacao")
=======
        st.query_params["page"] = "recomendacao"
>>>>>>> d898103 (feat: integrate amnesia dataset with HEXAD-based challenge recommendations)


def tela_recomendacao():
    st.title("🎯 Desafios Personalizados")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Dados Cadastrados")
        dados_resumo = {
            "Usuário": st.session_state.dados.get("usuario"),
            "Idade": st.session_state.dados.get("age"),
            "Objetivo": st.session_state.dados.get("goal"),
            "Nível": st.session_state.dados.get("experience_level"),
            "Dias de treino": st.session_state.dados.get("training_days"),
            "Tempo de treino": f"{st.session_state.dados.get('training_time')} min"
        }
        st.json(dados_resumo)

    with col2:
        st.subheader("🤖 Desafios Recomendados")
        try:
            response = requests.post(
                "http://localhost:8000/recomendar",
                json=st.session_state.dados
            )
            if response.status_code == 200:
                recomendacao = response.json()
                st.success(f"✅ {recomendacao['total_desafios']} desafios encontrados!")
                
                # Exibir desafios
                for i, desafio in enumerate(recomendacao['desafios'], 1):
                    with st.expander(f"🎯 Desafio {i}: {desafio['name']}"):
                        st.write(f"**Descrição:** {desafio['description']}")
                        st.write(f"**Tipo HEXAD:** {desafio['hexad_type']}")
                        st.write(f"**Dificuldade:** {desafio['difficulty']}")
                        st.write(f"**ID:** {desafio['id']}")
                
                st.session_state.recomendacao = recomendacao
                
            else:
                st.error(f"Erro {response.status_code} ao obter recomendação.")
                st.text(response.text)
        except Exception as e:
            st.error(f"Erro de conexão: {str(e)}")
            st.info("Certifique-se de que o servidor está rodando em http://localhost:8000")

    st.markdown("### Deseja avaliar a recomendação?")
    if st.button("👉 Avaliar Recomendação"):
<<<<<<< HEAD
        st.experimental_set_query_params(page="avaliacao")
=======
        st.query_params["page"] = "avaliacao"
>>>>>>> d898103 (feat: integrate amnesia dataset with HEXAD-based challenge recommendations)


def tela_avaliacao():
    st.title("⭐ Avaliação dos Desafios")

    if 'recomendacao' not in st.session_state:
        st.error("Nenhuma recomendação encontrada. Volte e gere uma recomendação primeiro.")
        if st.button("Voltar"):
            st.query_params["page"] = "recomendacao"
        return

    st.subheader("📊 Como você avalia os desafios recomendados?")

    success = st.slider("Sucesso na execução (0-10)", 0, 10, 5)
    streak = st.slider("Sequência de dias consecutivos (0-30)", 0, 30, 0)
    progress_pct = st.slider("Progresso geral (%)", 0, 100, 50)
    rating = st.slider("Avaliação geral (1-5)", 1, 5, 3)
    time = st.number_input("Tempo gasto (minutos)", min_value=0, max_value=300, step=5)

    if st.button("Enviar Avaliação"):
        dados_avaliacao = {
            "usuario": st.session_state.dados["usuario"],
            "senha": st.session_state.dados["senha"],
            "success": success,
            "streak": streak,
            "progress_pct": progress_pct,
            "rating": rating,
            "time": time
        }

        try:
            response = requests.post(
                "http://localhost:8000/avaliar",
                json=dados_avaliacao
            )
            if response.status_code == 200:
                st.success("✅ Avaliação enviada com sucesso!")
                st.json(response.json())
            else:
                st.error(f"Erro {response.status_code} ao enviar avaliação.")
                st.text(response.text)
        except Exception as e:
            st.error(f"Erro de conexão: {str(e)}")

    if st.button("🔄 Nova Recomendação"):
        st.query_params["page"] = "recomendacao"
