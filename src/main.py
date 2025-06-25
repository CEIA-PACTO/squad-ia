from fastapi import FastAPI
from src.endpoint.formulario import UsuarioInput, AvaliacaoInput
from src.endpoint.recomendador import recomendar, avaliar

app = FastAPI()

@app.post("/recomendar")
def post_recomendar(usuario: UsuarioInput):
    return recomendar(usuario)

@app.post("/avaliar")
def post_avaliar(avaliacao: AvaliacaoInput):
    return avaliar(avaliacao)
