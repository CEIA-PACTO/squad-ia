import pandas as pd
import datetime
import random
import hashlib
from pathlib import Path
from fastapi import HTTPException
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from src.endpoint.formulario import UsuarioInput, AvaliacaoInput

# === Caminhos ===
base_dir = Path(__file__).resolve().parents[2]
dados_path = base_dir / 'src' / 'dataframe' / 'gym recommendation.xlsx'

# === Dados ===
dados = pd.read_excel(dados_path)
dados.drop(columns=['Diet', "ID"], inplace=True)
dados.columns = [
    'Sexo', 'Idade', 'Altura', 'Peso', 'Hipertensao', 'Diabetes', 'IMC',
    'Nivel', 'Objetivo', 'Tipo_Fitness', 'Exercicios', 'Dieta', 'Equipamento'
]

label_enc = LabelEncoder()
for col in ['Sexo', 'Hipertensao', 'Diabetes', 'Nivel', 'Objetivo', 'Tipo_Fitness']:
    dados[col] = label_enc.fit_transform(dados[col])

scaler = StandardScaler()
dados[['Idade', 'Altura', 'Peso', 'IMC']] = scaler.fit_transform(
    dados[['Idade', 'Altura', 'Peso', 'IMC']]
)

colunas_features = [
    'Sexo', 'Idade', 'Altura', 'Peso', 'Hipertensao', 'Diabetes', 'IMC',
    'Nivel', 'Objetivo', 'Tipo_Fitness'
]

X = dados[colunas_features]
y_exercicio = dados['Exercicios']
y_equip = dados['Equipamento']

recomendacoes_fixas = [
    {'Exercicio': 'Treino Funcional', 'Equipamento': 'Elásticos de resistência'},
    {'Exercicio': 'HIIT', 'Equipamento': 'Esteira'},
    {'Exercicio': 'Pilates', 'Equipamento': 'Bola suíça'},
    {'Exercicio': 'Musculação', 'Equipamento': 'Halteres'},
    {'Exercicio': 'CrossFit', 'Equipamento': 'Caixa pliométrica'}
]

def gerar_id(usuario: str, senha: str) -> str:
    return hashlib.sha256((usuario + senha).encode('utf-8')).hexdigest()

def recomendar(usuario_input: UsuarioInput):
    dados_dict = usuario_input.dict()
    usuario = dados_dict['usuario']
    senha = dados_dict['senha']
    id_hash = gerar_id(usuario, senha)

    entrada_sem_senha = dados_dict.copy()
    entrada_sem_senha.pop('senha')

    entrada_df = pd.DataFrame([dados_dict])
    entrada_df[['Idade', 'Altura', 'Peso', 'IMC']] = scaler.transform(
        entrada_df[['Idade', 'Altura', 'Peso', 'IMC']]
    )
    entrada_features = entrada_df[colunas_features]

    usar_dicionario = random.random() < 0.2
    if usar_dicionario:
        rec = random.choice(recomendacoes_fixas)
        rec_ex = rec['Exercicio']
        rec_equip = rec['Equipamento']
    else:
        scores_sim = cosine_similarity(X, entrada_features).flatten()
        idx_top = scores_sim.argsort()[-5:][::-1]
        dados_similares = dados.iloc[idx_top]
        rec_ex = dados_similares['Exercicios'].mode()[0]
        rec_equip = dados_similares['Equipamento'].mode()[0]

    registro = {
        'id': id_hash,
        'Data_Hora': datetime.datetime.now().isoformat(),
        **entrada_sem_senha,
        'Recomendacao_Exercicio': rec_ex,
        'Recomendacao_Equipamento': rec_equip,
        'Recomendacao_Fixa_Usada': usar_dicionario
    }

    csv_path = base_dir / "registro_recomendacoes.csv"
    df_saida = pd.DataFrame([registro])
    if csv_path.exists():
        df_saida.to_csv(csv_path, mode='a', header=False, index=False)
    else:
        df_saida.to_csv(csv_path, index=False)

    return {"id": id_hash, "Recomendacao_Exercicio": rec_ex, "Recomendacao_Equipamento": rec_equip}

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
        'Recomendacao_Exercicio': ultima['Recomendacao_Exercicio'],
        'Recomendacao_Equipamento': ultima['Recomendacao_Equipamento'],
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
