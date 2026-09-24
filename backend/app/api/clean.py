from fastapi import APIRouter

from app.schemas.clean import CleanRequest
from app.core.text_cleaner import limpar_texto_bruto

router = APIRouter(prefix="/api/v1", tags=["limpeza"])


@router.post("/clean")
def clean(req: CleanRequest):
    entrada = req.texto
    saida = limpar_texto_bruto(entrada)
    print(f"[CLEAN] ENTRADA: {repr(entrada[:200])}")
    print(f"[CLEAN] SAIDA:   {repr(saida[:200])}")
    return {"texto_limpo": saida}