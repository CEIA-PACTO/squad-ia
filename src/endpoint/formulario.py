from pydantic import BaseModel
from typing import Optional


class UsuarioInput(BaseModel):
    # Dados básicos de autenticação
    usuario: str
    senha: str

    # Dados demográficos e físicos (baseados no amnesia dataset)
    age: int  # Idade
    height: float  # Altura em cm
    weight: float  # Peso em kg
    body_type: str  # "Masculino" ou "Feminino"

    # Dados de fitness (do amnesia dataset)
    goal: str  # "Emagrecimento", "Hipertrofia", "Força"
    training_days: int  # Dias de treino por semana
    training_time: int  # Tempo de treino em minutos
    experience_level: str  # "Iniciante", "Intermediário", "Avançado"

    # Scores HEXAD (do sim_dataset)
    score_philanthropist: float  # Score 0-7
    score_socialiser: float  # Score 0-7
    score_achiever: float  # Score 0-7
    score_player: float  # Score 0-7
    score_free_spirit: float  # Score 0-7
    score_disruptor: float  # Score 0-7


class AvaliacaoInput(BaseModel):
    usuario: str
    senha: str
    success: int  # Score de sucesso 0-10
    streak: int
    progress_pct: float
    rating: int
    time: int


# Mapeamentos para conversão entre formatos
HEXAD_MAPPING = {
    "conquistador": "Achiever",
    "jogador": "Player",
    "filantropo": "Philanthropist",
    "socializador": "Socialiser",
    "livre": "Free Spirit",
    "disruptor": "Disruptor"
}

REVERSE_HEXAD_MAPPING = {v: k for k, v in HEXAD_MAPPING.items()}

# Mapeamento de objetivos fitness
FITNESS_GOAL_MAPPING = {
    "Emagrecimento": "Emagrecimento",
    "Hipertrofia": "Hipertrofia",
    "Força": "Força"
}

# Mapeamento de níveis de experiência
EXPERIENCE_LEVEL_MAPPING = {
    "Iniciante": "Iniciante",
    "Intermediário": "Intermediário",
    "Avançado": "Avançado"
}


def convert_interface_to_amnesia_format(interface_data: dict) -> dict:
    """
    Converte dados da interface atual para o formato do dataset amnesia
    """
    # Converter dados de fitness
    objetivo_mapping = {
        1: "Emagrecimento",
        2: "Hipertrofia",
        3: "Força",
        4: "Condicionamento"
    }

    nivel_mapping = {
        1: "Iniciante",
        2: "Intermediário",
        3: "Avançado"
    }

    sexo_mapping = {
        1: "Masculino",
        2: "Feminino",
        3: "Feminino"  # Default para "Outro"
    }

    return {
        'usuario': interface_data.get('usuario', ''),
        'senha': interface_data.get('senha', ''),
        'age': int(interface_data.get('Idade', 25)),
        'height': float(interface_data.get('Altura', 1.70)) * 100,  # Converter metros para cm
        'weight': float(interface_data.get('Peso', 70)),
        'body_type': sexo_mapping.get(interface_data.get('Sexo', 2), "Feminino"),
        'goal': objetivo_mapping.get(interface_data.get('Objetivo', 1), "Emagrecimento"),
        'training_days': 3,  # Default baseado no dataset
        'training_time': 60,  # Default baseado no dataset
        'experience_level': nivel_mapping.get(interface_data.get('Nivel', 1), "Iniciante"),
        'score_philanthropist': 3.5,  # Default scores
        'score_socialiser': 3.5,
        'score_achiever': 3.5,
        'score_player': 3.5,
        'score_free_spirit': 3.5,
        'score_disruptor': 3.5
    }

def get_dominant_hexad_type(hexad_scores: dict) -> str:
    """
    Determina o tipo HEXAD dominante baseado nos scores
    """
    scores = {
        'Achiever': hexad_scores.get('score_achiever', 0),
        'Player': hexad_scores.get('score_player', 0),
        'Philanthropist': hexad_scores.get('score_philanthropist', 0),
        'Socialiser': hexad_scores.get('score_socialiser', 0),
        'Free Spirit': hexad_scores.get('score_free_spirit', 0),
        'Disruptor': hexad_scores.get('score_disruptor', 0)
    }

    return max(scores, key=scores.get)