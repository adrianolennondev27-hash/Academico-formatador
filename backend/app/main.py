import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import upload, clean, abnt, validation, convert

app = FastAPI(
    title="Formatador e Validador Acadêmico",
    description=(
        "API para limpeza, conversão, formatação ABNT e validação de textos."
    ),
    version="1.1.0",
)

# CORS — permite desenvolvimento local + produção (Vercel)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Adiciona a URL de produção do Vercel (definida em env var)
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas
app.include_router(clean.router)
app.include_router(upload.router)
app.include_router(abnt.router)
app.include_router(validation.router)
app.include_router(convert.router)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "mensagem": "API do Formatador e Validador Acadêmico rodando",
        "versao": "1.1.0",
    }