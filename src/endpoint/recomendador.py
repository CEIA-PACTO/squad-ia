import json
import random
import hashlib
import datetime
import traceback
import pandas as pd
from pathlib import Path
from fastapi import HTTPException
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

from src.endpoint.formulario import UsuarioInput, AvaliacaoInput
from src.models.postgrees import DatabaseInitializer

base_dir = Path(__file__).resolve().parents[2]
db = DatabaseInitializer(host="localhost", dbname="gameficacao", user="admin", password="admin")

desafios_por_hexad = {
        'Player': [1, 2, 3, 4, 5, 6, 7],
        'Socialiser': [8, 9, 10, 11, 24],
        'Free Spirit': [12, 13],
        'Achiever': [14, 15, 20, 21, 22, 23],
        'Philanthropist': [16, 17],
        'Disruptor': [18, 19]
    }
# ----------------------------------------------------------------------------------------------------------------------
def gym_recomendation():
    dados_path = base_dir / 'src' / 'dataframe' / 'amnesia_dataset.csv'
    # === Carregar dados da amnesia ===
    dados = pd.read_csv(dados_path)

    # === Pré-processamento dos dados da amnesia ===
    # Mapear colunas categóricas para numéricas
    label_enc = LabelEncoder()

    # Mapear fitness_goal
    dados['fitness_goal_encoded'] = label_enc.fit_transform(dados['fitness_goal'])

    # Mapear experience_level
    dados['experience_level_encoded'] = label_enc.fit_transform(dados['experience_level'])

    # Mapear body_type
    dados['body_type_encoded'] = label_enc.fit_transform(dados['body_type'])

    # Mapear dominant_hexad
    dados['dominant_hexad_encoded'] = label_enc.fit_transform(dados['dominant_hexad'])

    # Normalizar features numéricas
    scaler = StandardScaler()
    dados[['age', 'training_days', 'training_time']] = scaler.fit_transform(
        dados[['age', 'training_days', 'training_time']]
    )

    # Features para similaridade
    colunas_features = [
        'fitness_goal_encoded', 'experience_level_encoded', 'body_type_encoded',
        'age', 'training_days', 'training_time', 'dominant_hexad_encoded',
        'Philanthropist', 'Socialiser', 'Achiever', 'Player', 'Free Spirit', 'Disruptor'
    ]

    X = dados[colunas_features]
    return dados, X

def gerar_id(usuario: str, senha: str) -> str:
    return hashlib.sha256((usuario + senha).encode('utf-8')).hexdigest()

def recomendar(usuario_input):

    try:
        challenges_path = base_dir / 'src' / 'dataframe' / 'challenges.json'
        challenges_data = json.load(open(challenges_path, 'r'))
        df_challenges = pd.DataFrame(challenges_data)

        dados_dict = usuario_input.dict()
        usuario = dados_dict['usuario']
        senha = dados_dict['senha']

        id_hash = gerar_id(usuario, senha)
        entrada_sem_senha = dados_dict.copy()


        # Determinar perfil HEXAD dominante baseado nos scores
        hexad_scores = {
            'Philanthropist': dados_dict.get('score_philanthropist', 0),
            'Socialiser': dados_dict.get('score_socialiser', 0),
            'Achiever': dados_dict.get('score_achiever', 0),
            'Player': dados_dict.get('score_player', 0),
            'Free Spirit': dados_dict.get('score_free_spirit', 0),
            'Disruptor': dados_dict.get('score_disruptor', 0)
        }

        # Encontrar o tipo HEXAD com maior score
        hexad_dominante = max(hexad_scores, key=hexad_scores.get)

        # Selecionar desafios baseados no perfil HEXAD
        desafios_disponiveis = desafios_por_hexad.get(hexad_dominante, [])

        if desafios_disponiveis:
            # Selecionar um desafio aleatório do tipo HEXAD dominante
            challenge_id = random.choice(desafios_disponiveis)
            desafio = df_challenges[df_challenges['challenge_id'] == challenge_id].iloc[0]

            rec_desafio = desafio['description']
            rec_tipo = desafio['type']
            rec_duracao = desafio['duration']
            rec_sessoes = desafio['target_sessions']
        else:
            # Fallback para um desafio genérico
            desafio = df_challenges.iloc[0]
            rec_desafio = desafio['description']
            rec_tipo = desafio['type']
            rec_duracao = desafio['duration']
            rec_sessoes = desafio['target_sessions']

        registro = {
            'id': id_hash,
            'Data_Hora': datetime.datetime.now().isoformat(),
            **entrada_sem_senha,
            'hexad_dominante': hexad_dominante,
            'Recomendacao_Desafio': rec_desafio,
            'Recomendacao_Tipo': rec_tipo,
            'Recomendacao_Duracao': rec_duracao,
            'Recomendacao_Sessoes': rec_sessoes
        }

        csv_path = base_dir / "registro_recomendacoes.csv"
        df_saida = pd.DataFrame([registro])
        if csv_path.exists():
            df_saida.to_csv(csv_path, mode='a', header=False, index=False)
        else:
            df_saida.to_csv(csv_path, index=False)

        return {
            "id": id_hash,
            "hexad_dominante": hexad_dominante,
            "Recomendacao_Desafio": rec_desafio,
            "Recomendacao_Tipo": rec_tipo,
            "Recomendacao_Duracao": int(rec_duracao),
            "Recomendacao_Sessoes": int(rec_sessoes)
        }

    except Exception as e:
        return {"error": str(e)}

def avaliar(avaliacao_input: AvaliacaoInput):
    import datetime
    import pandas as pd
    from fastapi import HTTPException

    dados_dict = avaliacao_input.dict()
    usuario = dados_dict['usuario']
    senha = dados_dict['senha']

    print("aaa", usuario, senha)
    id_hash = gerar_id(usuario, senha)
    print("id", id_hash)

    rec_csv = base_dir / "registro_recomendacoes.csv"
    if not rec_csv.exists():
        raise HTTPException(status_code=404, detail="Nenhuma recomendação registrada ainda.")

    df_rec = pd.read_csv(rec_csv)
    print(df_rec)
    df_user = df_rec[df_rec['id'] == id_hash]
    if df_user.empty:
        raise HTTPException(status_code=404, detail="Nenhuma recomendação encontrada para este usuário.")

    ultima = df_user.iloc[-1].to_dict()
    print("ultima:", ultima)

    avaliacao = {
        'id': id_hash,
        'Data_Hora_Avaliacao': datetime.datetime.now().isoformat(),
        'Recomendacao_Desafio': ultima.get('Recomendacao_Desafio'),
        'Recomendacao_Tipo': ultima.get('Recomendacao_Tipo'),
        'Recomendacao_Duracao': ultima.get('Recomendacao_Duracao'),
        'Recomendacao_Sessoes': ultima.get('Recomendacao_Sessoes'),
        'success': dados_dict['success'],
        'streak': dados_dict['streak'],
        'progress_pct': dados_dict['progress_pct'],
        'rating': dados_dict['rating'],
        'time': dados_dict['time']
    }

    aval_csv = base_dir / "avaliacoes.csv"
    df_aval = pd.DataFrame([avaliacao])
    if aval_csv.exists():
        df_aval.to_csv(aval_csv, mode='a', header=False, index=False)
    else:
        df_aval.to_csv(aval_csv, index=False)

    return {"mensagem": "Avaliação registrada com sucesso.", "id": id_hash}
