import re
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.abnt import MetadadosABNT
from app.abnt.formatter import gerar_documento_abnt, _separar_nomes
from app.abnt.pdf_converter import converter_docx_para_pdf

router = APIRouter(prefix="/api/v1", tags=["abnt"])


def _nome_arquivo(titulo: str, ext: str) -> str:
    limpo = re.sub(r'[^\w\s-]', '', titulo).strip().replace(" ", "_")
    return f"{limpo or 'trabalho'}_ABNT.{ext}"


@router.post("/gerar-abnt")
def gerar_abnt(dados: MetadadosABNT):
    try:
        metadados = dados.model_dump()
        metadados["aluno"] = metadados.get("aluno", "").strip()
        print(f"[ABNT] ALUNO RECEBIDO: {repr(metadados.get('aluno'))}")
        print(f"[ABNT] SEPARADO:       {_separar_nomes(metadados['aluno'])}")
        texto = metadados.pop("texto_limpo")
        buffer_docx = gerar_documento_abnt(metadados, texto)
        headers = {
            "Content-Disposition":
                f'attachment; filename="{_nome_arquivo(metadados["titulo"], "docx")}"'
        }
        return StreamingResponse(
            buffer_docx,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers=headers,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@router.post("/gerar-abnt-pdf")
def gerar_abnt_pdf(dados: MetadadosABNT):
    try:
        metadados = dados.model_dump()
        metadados["aluno"] = metadados.get("aluno", "").strip()
        print(f"[ABNT-PDF] ALUNO RECEBIDO: {repr(metadados.get('aluno'))}")
        print(f"[ABNT-PDF] SEPARADO:       {_separar_nomes(metadados['aluno'])}")
        texto = metadados.pop("texto_limpo")
        buffer_docx = gerar_documento_abnt(metadados, texto)
        buffer_pdf = converter_docx_para_pdf(buffer_docx)
        headers = {
            "Content-Disposition":
                f'attachment; filename="{_nome_arquivo(metadados["titulo"], "pdf")}"'
        }
        return StreamingResponse(
            buffer_pdf, media_type="application/pdf", headers=headers
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(e)}")