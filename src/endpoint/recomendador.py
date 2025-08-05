import pandas as pd
import datetime
import random
import hashlib
import json
import ast
from pathlib import Path
from fastapi import HTTPException
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from src.endpoint.formulario import UsuarioInput, AvaliacaoInput
import logging

# === Caminhos ===
base_dir = Path(__file__).resolve().parents[2]
dados_path = base_dir / 'src' / 'dataframe' / 'recommendation_dataset.csv'
challenges_path = base_dir / 'src' / 'dataframe' / 'challenges.json'

# Carregar dados de recomendação
dados = pd.read_csv(dados_path)

# Carregar desafios
with open(challenges_path, 'r', encoding='utf-8') as f:
    challenges_list = json.load(f)

# Converter lista de desafios para dicionário por ID
challenges_data = {}
for challenge in challenges_list:
    challenges_data[challenge['challenge_id']] = challenge

# Preparar dados para similaridade
colunas_features = [
    'age', 'training_days', 'training_time',
    'Philanthropist', 'Socialiser', 'Free Spirit',
    'Achiever', 'Player', 'Disruptor'
]

# Normalizar dados numéricos
scaler = StandardScaler()
dados[['age', 'training_days', 'training_time']] = scaler.fit_transform(
    dados[['age', 'training_days', 'training_time']]
)

# Codificar variáveis categóricas
label_encoders = {}
categorical_cols = ['body_type', 'fitness_goal', 'experience_level']

for col in categorical_cols:
    label_encoders[col] = LabelEncoder()
    dados[f'{col}_encoded'] = label_encoders[col].fit_transform(dados[col])

# Adicionar colunas codificadas às features
colunas_features.extend([f'{col}_encoded' for col in categorical_cols])

X = dados[colunas_features]

def gerar_id(usuario: str, senha: str) -> str:
    return hashlib.sha256((usuario + senha).encode('utf-8')).hexdigest()

def get_challenge_details(challenge_ids):
    """Retorna detalhes dos desafios baseado nos IDs"""
    challenges = []
    for challenge_id in challenge_ids:
        if challenge_id in challenges_data:
            challenge = challenges_data[challenge_id]
            challenges.append({
                'id': challenge_id,
                'name': f"Desafio {challenge_id}",
                'description': challenge['description'],
                'hexad_type': challenge['type'],
                'difficulty': f"{challenge['duration']} dias, {challenge['target_sessions']} sessões"
            })
    return challenges

def recomendar(usuario_input):
    try:
        dados_dict = usuario_input.dict()
        usuario = dados_dict['usuario']
        senha = dados_dict['senha']

        id_hash = gerar_id(usuario, senha)
        
        # Preparar dados do usuário para similaridade
        entrada_df = pd.DataFrame([dados_dict])
        
        # Normalizar dados numéricos
        entrada_df[['age', 'training_days', 'training_time']] = scaler.transform(
            entrada_df[['age', 'training_days', 'training_time']]
        )
        
        # Mapear scores HEXAD para os nomes corretos do dataset
        entrada_df['Philanthropist'] = dados_dict.get('score_philanthropist', 3.5)
        entrada_df['Socialiser'] = dados_dict.get('score_socialiser', 3.5)
        entrada_df['Free Spirit'] = dados_dict.get('score_free_spirit', 3.5)
        entrada_df['Achiever'] = dados_dict.get('score_achiever', 3.5)
        entrada_df['Player'] = dados_dict.get('score_player', 3.5)
        entrada_df['Disruptor'] = dados_dict.get('score_disruptor', 3.5)
        
        # Mapear dados categóricos para os valores do dataset
        # Mapeamento de goal para fitness_goal
        goal_mapping = {
            'Emagrecimento': 'Emagrecimento',
            'Hipertrofia': 'Hipertrofia', 
            'Força': 'Força'
        }
        entrada_df['fitness_goal'] = goal_mapping.get(dados_dict.get('goal', 'Emagrecimento'), 'Emagrecimento')
        
        # Mapeamento de experience_level
        level_mapping = {
            'Iniciante': 'Iniciante',
            'Intermediário': 'Intermediário',
            'Avançado': 'Avançado'
        }
        entrada_df['experience_level'] = level_mapping.get(dados_dict.get('experience_level', 'Iniciante'), 'Iniciante')
        
        # Mapeamento de body_type
        body_mapping = {
            'Masculino': 'Masculino',
            'Feminino': 'Feminino'
        }
        entrada_df['body_type'] = body_mapping.get(dados_dict.get('body_type', 'Masculino'), 'Masculino')
        
        # Codificar dados categóricos
        for col in categorical_cols:
            entrada_df[f'{col}_encoded'] = label_encoders[col].transform(entrada_df[col])
        
        entrada_features = entrada_df[colunas_features]

        # Calcular similaridade
        scores_sim = cosine_similarity(X, entrada_features).flatten()
        idx_top = scores_sim.argsort()[-3:][::-1]  # Top 3 usuários similares
        
        print(f"DEBUG: Top 3 índices similares: {idx_top}")
        print(f"DEBUG: Scores de similaridade: {scores_sim[idx_top]}")
        
        # Pegar desafios recomendados dos usuários similares
        desafios_recomendados = []
        for idx in idx_top:
            user_challenges = dados.iloc[idx]['recommended_challenges']
            print(f"DEBUG: Usuário {idx} - desafios: {user_challenges}")
            if pd.notna(user_challenges) and user_challenges:
                # Converter string de lista para lista real usando ast.literal_eval
                if isinstance(user_challenges, str):
                    try:
                        challenges_list = ast.literal_eval(user_challenges)
                        print(f"DEBUG: Lista convertida: {challenges_list}")
                        if isinstance(challenges_list, list):
                            desafios_recomendados.extend(challenges_list)
                    except Exception as e:
                        print(f"DEBUG: Erro ao converter: {e}")
                        continue
                else:
                    desafios_recomendados.extend(user_challenges)
        
        print(f"DEBUG: Desafios coletados: {desafios_recomendados}")
        
        # Remover duplicatas e pegar top 5
        desafios_unicos = list(set(desafios_recomendados))[:5]
        print(f"DEBUG: Desafios únicos: {desafios_unicos}")
        
        # Se não houver desafios suficientes, adicionar alguns aleatórios
        if len(desafios_unicos) < 3:
            all_challenge_ids = list(challenges_data.keys())
            desafios_aleatorios = random.sample(all_challenge_ids, 3 - len(desafios_unicos))
            desafios_unicos.extend(desafios_aleatorios)
            print(f"DEBUG: Adicionados desafios aleatórios: {desafios_aleatorios}")
        
        # Obter detalhes dos desafios
        desafios_detalhados = get_challenge_details(desafios_unicos)
        print(f"DEBUG: Desafios detalhados: {len(desafios_detalhados)}")
        
        registro = {
            'id': id_hash,
            'Data_Hora': datetime.datetime.now().isoformat(),
            'usuario': usuario,
            'age': dados_dict.get('age'),
            'body_type': dados_dict.get('body_type'),
            'fitness_goal': dados_dict.get('goal'),
            'experience_level': dados_dict.get('experience_level'),
            'Recomendacao_Desafios': desafios_unicos,
            'Numero_Desafios': len(desafios_unicos)
        }

        # Salvar registro
        csv_path = base_dir / "registro_recomendacoes.csv"
        df_saida = pd.DataFrame([registro])
        if csv_path.exists():
            df_saida.to_csv(csv_path, mode='a', header=False, index=False)
        else:
            df_saida.to_csv(csv_path, index=False)

        return {
            "id": id_hash, 
            "desafios": desafios_detalhados,
            "total_desafios": len(desafios_detalhados)
        }
        
    except Exception as e:
        logging.error(f"Erro na recomendação: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

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
        'usuario': usuario,
        'Recomendacao_Desafios': ultima.get('Recomendacao_Desafios', ''),
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