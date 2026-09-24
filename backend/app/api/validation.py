from fastapi import APIRouter
from pydantic import BaseModel

from app.validators.spelling import verificar_ortografia
from app.validators.grammar import verificar_gramatica
from app.validators.structure import validar_estrutura

router = APIRouter(prefix="/api/v1", tags=["validação"])


class TextoRequest(BaseModel):
    texto: str


class EstruturaRequest(BaseModel):
    texto: str
    tipo_trabalho: str


@router.post("/validar")
def validar_texto(req: TextoRequest):
    erros_ortografia = verificar_ortografia(req.texto)
    erros_gramatica = verificar_gramatica(req.texto)

    total_erros = len(erros_ortografia) + len(erros_gramatica)

    return {
        "status": "sucesso",
        "total_alertas": total_erros,
        "ortografia": erros_ortografia,
        "gramatica": erros_gramatica
    }


@router.post("/validar-estrutura")
def validar_estrutura_endpoint(req: EstruturaRequest):
    alertas = validar_estrutura(req.texto, req.tipo_trabalho.lower())
    return {
        "status": "sucesso",
        "tipo_trabalho": req.tipo_trabalho,
        "total_alertas": len(alertas),
        "alertas": alertas
    }