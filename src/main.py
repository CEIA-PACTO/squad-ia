from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, HTTPException
from src.endpoint.formulario import UsuarioInput, AvaliacaoInput
from src.endpoint.recomendador import executar_recomendacao
from fastapi.staticfiles import StaticFiles
import hashlib
from src.endpoint.recomendador import executar_recomendacao

app = FastAPI()

templates = Jinja2Templates(directory="src/templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/questionario")
async def questionario(usuario: str = Form(...), senha: str = Form(...)):
    return RedirectResponse(f"/questionario?usuario={usuario}&senha={senha}", status_code=303)


@app.get("/questionario", response_class=HTMLResponse)
async def questionario_form(request: Request, usuario: str, senha: str):
    context = {"request": request, "usuario": usuario, "senha": senha}
    return templates.TemplateResponse("questionario.html", context)


@app.post("/recomendar-form", response_class=HTMLResponse)
async def recomendar_form(
    request: Request,
    usuario: str = Form(...),
    senha: str = Form(...),
    persona_primaria: str = Form(...),
    persona_secundaria: str = Form(...),
    importancia_amigos: int = Form(...),
    importancia_resultados: int = Form(...),
    importancia_diversao: int = Form(...),
    Sexo: int = Form(...),
    Idade: float = Form(...),
    Altura: float = Form(...),
    Peso: float = Form(...),
    Hipertensao: int = Form(...),
    Diabetes: int = Form(...),
    IMC: float = Form(...),
    Nivel: int = Form(...),
    Objetivo: int = Form(...),
    Tipo_Fitness: int = Form(...),
):
    dados = UsuarioInput(
        usuario=usuario,
        senha=senha,
        Sexo=Sexo,
        Idade=Idade,
        Altura=Altura,
        Peso=Peso,
        Hipertensao=Hipertensao,
        Diabetes=Diabetes,
        IMC=IMC,
        Nivel=Nivel,
        Objetivo=Objetivo,
        Tipo_Fitness=Tipo_Fitness,
        persona_primaria=persona_primaria,
        persona_secundaria=persona_secundaria,
        importancia_amigos=importancia_amigos,
        importancia_resultados=importancia_resultados,
        importancia_diversao=importancia_diversao,
    )

    rec = executar_recomendacao(dados)
    context = {
        "request": request,
        "usuario": usuario,
        "senha": senha,
        "recomendacao": rec,
    }
    return templates.TemplateResponse("recomendacao.html", context)


@app.post("/avaliar-form", response_class=HTMLResponse)
async def avaliar_form(
    request: Request,
    usuario: str = Form(...),
    senha: str = Form(...),
    success: str = Form(...),
    streak: int = Form(...),
    progress_pct: float = Form(...),
    rating: int = Form(...),
    time: int = Form(...),
):
    dados = AvaliacaoInput(
        usuario=usuario,
        senha=senha,
        success=True if success.lower() == "true" else False,
        streak=streak,
        progress_pct=progress_pct,
        rating=rating,
        time=time,
    )

    resp = avaliar(dados)
    context = {"request": request, **resp}
    return templates.TemplateResponse("avaliado.html", context)

import hashlib
from fastapi import HTTPException


def gerar_id(usuario: str | None, senha: str | None) -> str:
    base = f"{usuario or ''}{senha or ''}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

@app.post("/recomendar")
def post_recomendar(usuario: UsuarioInput):
    try:
        payload = usuario.dict()
        uid = gerar_id(payload.get("usuario"), payload.get("senha"))

        # opcional: não salvar senha em claro
        # payload.pop("senha", None)

        resultado = executar_recomendacao(
            user_id=uid,
            payload=payload,
            path_excel="../dataframe/gym_recommendation.xlsx",
            path_hist_csv="../bd/registro_recomendacoes.csv",
            path_challenger="../dataframe/challenger.json",
            random_rate=0.4,
            n_neighbors=50,
            top_n=5,
        )
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/avaliar")
def post_avaliar(avaliacao: AvaliacaoInput):
    return avaliar(avaliacao)
