import pandas as pd
import datetime
import random
import traceback
import hashlib
from pathlib import Path
from fastapi import HTTPException
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from src.endpoint.formulario import UsuarioInput, AvaliacaoInput
from src.models.postgrees import DatabaseInitializer


base_dir = Path(__file__).resolve().parents[2]
db = DatabaseInitializer(host="localhost", dbname="gameficacao", user="admin", password="admin")

colunas_features = ['Sexo', 'Idade', 'Altura', 'Peso', 'Hipertensao', 'Diabetes', 'IMC', 'Nivel', 'Objetivo', 'Tipo_Fitness']

def gym_recomendation():

    dados_path = base_dir /'src'/ 'dataframe' / 'gym_recommendation.xlsx'
    dados = pd.read_excel(dados_path)

    dados.drop(columns=['Diet', "ID"], inplace=True)
    dados.columns = ['Sexo', 'Idade', 'Altura', 'Peso', 'Hipertensao', 'Diabetes', 'IMC','Nivel', 'Objetivo', 'Tipo_Fitness', 'Exercicios', 'Dieta', 'Equipamento']

    label_enc = LabelEncoder()
    for col in ['Sexo', 'Hipertensao', 'Diabetes', 'Nivel', 'Objetivo', 'Tipo_Fitness']:
        dados[col] = label_enc.fit_transform(dados[col])

    X = dados[colunas_features]
    y_exercicio = dados['Exercicios']
    y_equip = dados['Equipamento']

    return dados, X


def gerar_id(usuario: str, senha: str) -> str:
    return hashlib.sha256((usuario + senha).encode('utf-8')).hexdigest()

def recomendar(usuario_input):
    try:
        # Carrega desafios fixos
        recomendacoes_fixas = pd.read_json(base_dir / 'src' / "dataframe" / "challenger.json")

        # Carrega base de dados e features
        dados, X = gym_recomendation()

        # Converte entrada para dicionário
        dados_dict = usuario_input.dict()
        print("=== DADOS DE ENTRADA ===")
        print(dados_dict)

        # Geração de ID
        usuario = dados_dict['usuario']
        senha = dados_dict['senha']
        id_hash = gerar_id(usuario, senha)

        # Remove senha para não salvar
        entrada_sem_senha = dados_dict.copy()
        entrada_sem_senha.pop('senha')

        # Monta DataFrame com as features
        entrada_df = pd.DataFrame([dados_dict])
        entrada_features = entrada_df[colunas_features]

        # Decide entre recomendação fixa ou baseada em similaridade
        usar_dicionario = random.random() < 0.99
        if usar_dicionario:
            rec = recomendacoes_fixas.sample(n=5).iloc[0]
            print("⚠️ Usando recomendação aleatória do challenger.json")

            rec_ex = rec['description']
            rec_equip = f"Complete {rec['target_sessions']} sessões em {rec['duration']} dias"
            desafio_info = rec.to_dict()

            return desafio_info

        else:
            # Calcula similaridade
            scores_sim = cosine_similarity(X, entrada_features).flatten()
            idx_top = scores_sim.argsort()[-5:][::-1]
            dados_similares = dados.iloc[idx_top]

            # Recomendação por maioria
            rec_ex = dados_similares['Exercicios'].mode()[0]
            rec_equip = dados_similares['Equipamento'].mode()[0]

        # Registro de recomendação
        registro = {
            'id': id_hash,
            'Data_Hora': datetime.datetime.now().isoformat(),
            **entrada_sem_senha,
            'Recomendacao_Exercicio': rec_ex,
            'Recomendacao_Equipamento': rec_equip,
            'Recomendacao_Fixa_Usada': usar_dicionario
        }

        # Salva recomendação em CSV
        csv_path = base_dir / "registro_recomendacoes.csv"
        df_saida = pd.DataFrame([registro])
        if csv_path.exists():
            df_saida.to_csv(csv_path, mode='a', header=False, index=False)
        else:
            df_saida.to_csv(csv_path, index=False)

        # Insere no banco
        # db.inserir_avaliacao(df_saida)

        # Retorno final
        resultado = {
            "id": id_hash,
            "Recomendacao_Exercicio": rec_ex,
            "Recomendacao_Equipamento": rec_equip
        }
        print("✅ RECOMENDAÇÃO GERADA:", resultado)
        return resultado

    except Exception as e:
        tb = traceback.format_exc()
        print("❌ Traceback completo:")
        print(tb)
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