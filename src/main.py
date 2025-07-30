from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from src.endpoint.formulario import UsuarioInput, AvaliacaoInput
from src.endpoint.recomendador import recomendar, avaliar
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="Squad IA - Sistema de Recomendação de Desafios", 
              description="API para recomendação de desafios fitness baseada em perfil HEXAD")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="src/templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Squad IA API está funcionando!"}

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
    # Scores HEXAD
    score_philanthropist: float = Form(...),
    score_socialiser: float = Form(...),
    score_free_spirit: float = Form(...),
    score_achiever: float = Form(...),
    score_player: float = Form(...),
    score_disruptor: float = Form(...),
    # Dados demográficos e fitness
    age: int = Form(...),
    height: float = Form(...),
    weight: float = Form(...),
    body_type: str = Form(...),
    goal: str = Form(...),
    training_days: int = Form(...),
    training_time: int = Form(...),
    experience_level: str = Form(...),
):
    dados = UsuarioInput(
        usuario=usuario,
        senha=senha,
        score_philanthropist=score_philanthropist,
        score_socialiser=score_socialiser,
        score_free_spirit=score_free_spirit,
        score_achiever=score_achiever,
        score_player=score_player,
        score_disruptor=score_disruptor,
        age=age,
        height=height,
        weight=weight,
        body_type=body_type,
        goal=goal,
        training_days=training_days,
        training_time=training_time,
        experience_level=experience_level,
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
    success: int = Form(...),
    streak: int = Form(...),
    progress_pct: float = Form(...),
    rating: int = Form(...),
    time: int = Form(...),
):
    dados = AvaliacaoInput(
        usuario=usuario,
        senha=senha,
        success=success,
        streak=streak,
        progress_pct=progress_pct,
        rating=rating,
        time=time,
    )

    resp = avaliar(dados)
    context = {"request": request, **resp}
    return templates.TemplateResponse("avaliado.html", context)

@app.post("/recomendar")
def post_recomendar(usuario: UsuarioInput):
    return recomendar(usuario)

@app.post("/avaliar")
def post_avaliar(avaliacao: AvaliacaoInput):
    return avaliar(avaliacao)