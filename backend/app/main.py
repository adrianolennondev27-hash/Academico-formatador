import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import upload, clean, abnt, validation, convert

app = FastAPI(
    title="Formatador e Validador Acadêmico",
    description="API para limpeza, conversão, formatação ABNT e validação de textos.",
    version="1.1.0",
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Exception handler: garante headers de CORS mesmo em erro 500
# ============================================================
@app.exception_handler(Exception)
async def catch_all_exception(request: Request, exc: Exception):
    origin = request.headers.get("origin", "*")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Erro interno: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


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