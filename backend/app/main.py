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

# CORS — em produção, troque "*" pelo domínio do seu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas
app.include_router(clean.router)
app.include_router(upload.router)
app.include_router(abnt.router)
app.include_router(validation.router)
app.include_router(convert.router)  # ← NOVO: conversão pura de formatos


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "mensagem": "API do Formatador e Validador Acadêmico rodando",
        "versao": "1.1.0",
    }