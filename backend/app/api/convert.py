"""
Módulo de CONVERSÃO PURA de formato.

Estratégia:
- DOCX → PDF: tenta dxpdf (leve). Se falhar, cai pro LibreOffice (robusto).
- PDF → DOCX: usa pdf2docx.
- Outras conversões: LibreOffice.
"""
import os
import shutil
import subprocess
import tempfile
import uuid
import re
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.abnt.pdf_converter import _encontrar_soffice

router = APIRouter(prefix="/api/v1", tags=["conversão"])


# ============================================================
# Mapa de conversões via LibreOffice
# ============================================================
CONVERSOES_LIBREOFFICE = {
    ("odt", "pdf"): "pdf",
    ("doc", "pdf"): "pdf",
    ("pdf", "odt"): "odt",
    ("doc", "docx"): "docx:MS Word 2007 XML",
    ("docx", "doc"): "doc:MS Word 97",
    ("doc", "odt"): "odt",
    ("docx", "odt"): "odt",
    ("odt", "docx"): "docx:MS Word 2007 XML",
    ("odt", "doc"): "doc:MS Word 97",
}

MIME_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "doc": "application/msword",
    "odt": "application/vnd.oasis.opendocument.text",
}

EXTENSOES_ACEITAS = {".pdf", ".doc", ".docx", ".odt"}


def _sanitizar_nome(nome: str) -> str:
    """Remove caracteres problemáticos do nome do arquivo."""
    nome = re.sub(r"[–—]", "-", nome)
    nome = re.sub(r"[""''']", "'", nome)
    nome = re.sub(r"[^\w\s\-\.]", "", nome, flags=re.UNICODE)
    return nome.strip() or "arquivo"


# ============================================================
# Conversores
# ============================================================

def _converter_docx_para_pdf_dxpdf(entrada: str, saida: str) -> bool:
    """
    Tenta converter DOCX → PDF com dxpdf (leve, rápido).
    Retorna True se funcionou, False se falhou.
    """
    try:
        import dxpdf
        dxpdf.convert_file(entrada, saida)
        if os.path.exists(saida) and os.path.getsize(saida) > 0:
            print("[CONVERT] dxpdf OK")
            return True
        print("[CONVERT] dxpdf gerou PDF vazio")
        return False
    except Exception as e:
        print(f"[CONVERT] dxpdf falhou: {e}")
        return False


def _converter_docx_para_pdf_libreoffice(entrada: str, tmpdir: str) -> str:
    """
    Fallback: converte DOCX → PDF com LibreOffice (pesado, robusto).
    Retorna o caminho do PDF gerado.
    """
    soffice = _encontrar_soffice()
    try:
        subprocess.run(
            [
                soffice,
                "--headless",
                "--norestore",
                "--nologo",
                "--nodefault",
                f"-env:UserInstallation=file://{tmpdir}/lo_profile",
                "--convert-to", "pdf",
                "--outdir", tmpdir,
                entrada,
            ],
            check=True,
            timeout=180,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Falha na conversão (LibreOffice): {(e.stderr or '')[:300]}",
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Timeout na conversão.")

    # Encontra o PDF gerado
    for nome in os.listdir(tmpdir):
        if nome.endswith(".pdf") and not nome.startswith("entrada_"):
            print("[CONVERT] LibreOffice OK")
            return os.path.join(tmpdir, nome)

    raise HTTPException(status_code=500, detail="LibreOffice não gerou o PDF.")


def _converter_pdf_para_docx(entrada: str, saida: str):
    """Converte PDF → DOCX usando pdf2docx."""
    try:
        from pdf2docx import Converter
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Biblioteca pdf2docx não instalada.",
        )
    try:
        cv = Converter(entrada)
        cv.convert(saida)
        cv.close()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao converter PDF (pdf2docx): {str(e)}",
        )


def _converter_com_libreoffice(soffice: str, entrada: str, tmpdir: str, filtro: str):
    """LibreOffice para conversões gerais (ODT, DOC antigos)."""
    try:
        subprocess.run(
            [
                soffice,
                "--headless",
                "--norestore",
                "--nologo",
                "--nodefault",
                f"-env:UserInstallation=file://{tmpdir}/lo_profile",
                "--convert-to", filtro,
                "--outdir", tmpdir,
                entrada,
            ],
            check=True,
            timeout=180,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Falha na conversão via LibreOffice: {(e.stderr or '')[:300]}",
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Timeout na conversão.")


# ============================================================
# Endpoint principal
# ============================================================

@router.post("/converter")
async def converter(
    file: UploadFile = File(...),
    formato_saida: str = Form(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    nome_original = _sanitizar_nome(file.filename)
    ext_entrada = Path(nome_original).suffix.lower()
    formato_saida = formato_saida.lower().strip().lstrip(".")

    if ext_entrada not in EXTENSOES_ACEITAS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{ext_entrada}' não suportado.",
        )

    if ext_entrada.lstrip(".") == formato_saida:
        raise HTTPException(
            status_code=400,
            detail="Formato de entrada e saída são iguais.",
        )

    chave_lo = (ext_entrada.lstrip("."), formato_saida)
    suportado_lo = chave_lo in CONVERSOES_LIBREOFFICE
    suportado_docx_pdf = (ext_entrada == ".docx" and formato_saida == "pdf")
    suportado_pdf2docx = (ext_entrada == ".pdf" and formato_saida in ("docx", "doc"))

    if not (suportado_lo or suportado_docx_pdf or suportado_pdf2docx):
        raise HTTPException(
            status_code=400,
            detail=f"Conversão {ext_entrada} → .{formato_saida} não é suportada.",
        )

    tmpdir = tempfile.mkdtemp(prefix="fva_conv_")
    try:
        entrada_path = os.path.join(tmpdir, f"entrada_{uuid.uuid4().hex}{ext_entrada}")
        with open(entrada_path, "wb") as f:
            f.write(await file.read())

        nome_base = Path(nome_original).stem
        saida_path = None

        # --- DOCX → PDF (fallback: dxpdf → LibreOffice) ---
        if suportado_docx_pdf:
            saida_dxpdf = os.path.join(tmpdir, f"{nome_base}.pdf")
            if _converter_docx_para_pdf_dxpdf(entrada_path, saida_dxpdf):
                saida_path = saida_dxpdf
            else:
                print("[CONVERT] dxpdf falhou, tentando LibreOffice...")
                saida_path = _converter_docx_para_pdf_libreoffice(entrada_path, tmpdir)
            formato_final = "pdf"

        # --- PDF → DOCX/DOC (pdf2docx) ---
        elif suportado_pdf2docx:
            formato_final = "docx"
            saida_path = os.path.join(tmpdir, f"{nome_base}.docx")
            _converter_pdf_para_docx(entrada_path, saida_path)

        # --- Outras (LibreOffice) ---
        elif suportado_lo:
            filtro = CONVERSOES_LIBREOFFICE[chave_lo]
            soffice = _encontrar_soffice()
            _converter_com_libreoffice(soffice, entrada_path, tmpdir, filtro)
            formato_final = formato_saida
            for nome in os.listdir(tmpdir):
                if nome.endswith(f".{formato_final}") and not nome.startswith("entrada_"):
                    saida_path = os.path.join(tmpdir, nome)
                    break

        if not saida_path or not os.path.exists(saida_path):
            raise HTTPException(
                status_code=500,
                detail="Arquivo convertido não foi gerado.",
            )

        with open(saida_path, "rb") as f:
            conteudo = f.read()

        nome_saida = f"{nome_base}.{formato_final}"

        return StreamingResponse(
            iter([conteudo]),
            media_type=MIME_TYPES.get(formato_final, "application/octet-stream"),
            headers={
                "Content-Disposition": f'attachment; filename="{nome_saida}"',
                "Content-Length": str(len(conteudo)),
            },
        )

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


@router.get("/converter/formatos")
def formatos_suportados():
    """Lista os pares de conversão suportados."""
    conversoes = list(CONVERSOES_LIBREOFFICE.keys())
    conversoes.append(("docx", "pdf"))
    conversoes.append(("pdf", "docx"))
    conversoes.append(("pdf", "doc"))
    return {"conversoes": [{"de": de, "para": para} for de, para in sorted(conversoes)]}