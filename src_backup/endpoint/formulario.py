from pydantic import BaseModel

class UsuarioInput(BaseModel):
    usuario: str
    senha: str
    Sexo: int
    Idade: float
    Altura: float
    Peso: float
    Hipertensao: int
    Diabetes: int
    IMC: float
    Nivel: int
    Objetivo: int
    Tipo_Fitness: int
    persona_primaria: str
    persona_secundaria: str
    importancia_amigos: int
    importancia_resultados: int
    importancia_diversao: int
    # Scores HEXAD adicionados
    score_philanthropist: float = 0.0
    score_socialiser: float = 0.0
    score_achiever: float = 0.0
    score_player: float = 0.0
    score_free_spirit: float = 0.0
    score_disruptor: float = 0.0

class AvaliacaoInput(BaseModel):
    usuario: str
    senha: str
    success: bool
    streak: int
    progress_pct: float
    rating: int
    time: int
