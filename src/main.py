from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.endpoint.formulario import UsuarioInput, AvaliacaoInput
from src.endpoint.recomendador import recomendar, avaliar
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import traceback

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("Erro de validação no endpoint:", request.url)
    print("Detalhes do erro:")
    traceback.print_exc()  # ou apenas: print(exc)
    return JSONResponse(
        status_code=422,
        content={"erro": "Erro de validação", "detalhes": exc.errors()},
    )

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

    rec = recomendar(dados)
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

import traceback

@app.post("/recomendar")
def post_recomendar(usuario: UsuarioInput):
    try:
        return recomendar(usuario)
    except Exception as e:
        print("Erro ao executar 'recomendar':")
        traceback.print_exc()  # Exibe o stack trace completo no terminal
        return {"erro": str(e)}


@app.post("/avaliar")
def post_avaliar(avaliacao: AvaliacaoInput):
    return avaliar(avaliacao)