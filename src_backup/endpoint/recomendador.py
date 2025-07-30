import pandas as pd
import datetime
import random
import hashlib
import json
from pathlib import Path
from fastapi import HTTPException
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from src.endpoint.formulario import UsuarioInput, AvaliacaoInput
import logging

# === Caminhos ===
base_dir = Path(__file__).resolve().parents[2]
dados_path = base_dir / 'src' / 'dataframe' / 'amnesia_dataset.csv'
challenges_path = base_dir / 'src' / 'dataframe' / 'challenges.json'

# === Carregar dados da amnesia ===
dados = pd.read_csv(dados_path)
challenges_data = json.load(open(challenges_path, 'r'))
df_challenges = pd.DataFrame(challenges_data)

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

# Desafios por tipo HEXAD
desafios_por_hexad = {
    'Player': [1, 2, 3, 4, 5, 6, 7],
    'Socialiser': [8, 9, 10, 11, 24],
    'Free Spirit': [12, 13],
    'Achiever': [14, 15, 20, 21, 22, 23],
    'Philanthropist': [16, 17],
    'Disruptor': [18, 19]
}

def gerar_id(usuario: str, senha: str) -> str:
    return hashlib.sha256((usuario + senha).encode('utf-8')).hexdigest()

def recomendar(usuario_input):
    try:
        dados_dict = usuario_input.dict()
        usuario = dados_dict['usuario']
        senha = dados_dict['senha']

        id_hash = gerar_id(usuario, senha)
        entrada_sem_senha = dados_dict.copy()
        entrada_sem_senha.pop('senha')
        
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
            "Recomendacao_Duracao": rec_duracao,
            "Recomendacao_Sessoes": rec_sessoes
        }
    except Exception as e:
        return {"error": str(e)}

def avaliar(avaliacao_input: AvaliacaoInput):
    dados_dict = avaliacao_input.dict()
    usuario = dados_dict['usuario']
    senha = dados_dict['senha']
    id_hash = gerar_id(usuario, senha)

    rec_csv = base_dir / "registro_recomendacoes.csv"
    if not rec_csv.exists():
        raise HTTPException(status_code=404, detail="Nenhuma recomendação registrada ainda.")

    df_rec = pd.read_csv(rec_csv)
    df_user = df_rec[df_rec['id'] == id_hash]
    if df_user.empty:
        raise HTTPException(status_code=404, detail="Nenhuma recomendação encontrada para este usuário.")

    ultima = df_user.iloc[-1].to_dict()

    avaliacao = {
        'id': id_hash,
        'Data_Hora_Avaliacao': datetime.datetime.now().isoformat(),
        'hexad_dominante': ultima.get('hexad_dominante', 'N/A'),
        'Recomendacao_Desafio': ultima.get('Recomendacao_Desafio', 'N/A'),
        'Recomendacao_Tipo': ultima.get('Recomendacao_Tipo', 'N/A'),
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