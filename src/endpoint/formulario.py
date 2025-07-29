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

class AvaliacaoInput(BaseModel):
    usuario: str
    senha: str
    success: bool
    streak: int
    progress_pct: float
    rating: int
    time: int
