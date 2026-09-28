"""
Módulo de CONVERSÃO PURA de formato.

- Não aplica margens, fontes, capa ou qualquer formatação ABNT.
- Apenas reempacota o arquivo em outro formato.
- Processamento stateless: arquivo existe só na RAM/pasta temporária.
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


CONVERSOES_SUPORTADAS: dict[tuple[str, str], str] = {
    ("docx", "pdf"): "pdf",
    ("doc", "pdf"): "pdf",
    ("odt", "pdf"): "pdf",
    ("pdf", "docx"): "PDF2DOCX",
    ("pdf", "doc"): "PDF2DOCX",
    ("pdf", "odt"): "odt",
    ("doc", "docx"): "docx:MS Word 2007 XML",
    ("docx", "doc"): "doc:MS Word 97",
    ("doc", "odt"): "odt",
    ("docx", "odt"): "odt",
    ("odt", "docx"): "docx:MS Word 2007 XML",
    ("odt", "doc"): "doc:MS Word 97",
}

MIME_TYPES: dict[str, str] = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "doc": "application/msword",
    "odt": "application/vnd.oasis.opendocument.text",
}

EXTENSOES_ACEITAS = {".pdf", ".doc", ".docx", ".odt"}


def _sanitizar_nome(nome: str) -> str:
    """
    Remove caracteres problemáticos do nome do arquivo:
    - Travessões (–, —) → hífen
    - Aspas curvas (" " ' ') → reto
    - Outros símbolos unicode → vazio
    
    Isso evita erro de encoding no subprocess do LibreOffice.
    """
    # Normaliza unicode (NFC)
    import unicodedata
    nome = unicodedata.normalize("NFC", nome)

    # Substitui travessões e aspas curvas
    nome = nome.replace("–", "-").replace("—", "-")
    nome = nome.replace(""", "\"").replace(""", "\"")
    nome = nome.replace("'", "'").replace("'", "'")

    # Remove outros caracteres não-ASCII problemáticos
    nome = re.sub(r"[^\w\s\-\.]", "", nome, flags=re.UNICODE)

    return nome.strip() or "arquivo"


def _converter_via_libreoffice(soffice: str, entrada: str, tmpdir: str, filtro: str):
    """Chama o LibreOffice headless para converter arquivos."""
    try:
        subprocess.run(
            [
                soffice,
                "--headless",
                "--norestore",
                "--nologo",
                "--nodefault",
                f"-env:UserInstallation=file://{tmpdir}/lo_profile",
                "--convert-to",
                filtro,
                "--outdir",
                tmpdir,
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
            detail=(
                "Falha na conversão via LibreOffice: "
                f"{(e.stderr or '')[:300] or 'erro desconhecido'}"
            ),
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=500,
            detail="Timeout na conversão (limite: 180s).",
        )


def _converter_via_pdf2docx(entrada: str, saida: str):
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
            detail=f"Falha ao converter PDF: {str(e)}",
        )


@router.post("/converter")
async def converter(
    file: UploadFile = File(...),
    formato_saida: str = Form(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    # Sanitiza o nome do arquivo (remove travessões, aspas curvas, etc.)
    nome_original = _sanitizar_nome(file.filename)
    ext_entrada = Path(nome_original).suffix.lower()
    formato_saida = formato_saida.lower().strip().lstrip(".")

    if ext_entrada not in EXTENSOES_ACEITAS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{ext_entrada}' não suportado. Aceitos: PDF, DOC, DOCX, ODT.",
        )

    if ext_entrada.lstrip(".") == formato_saida:
        raise HTTPException(
            status_code=400,
            detail="Formato de entrada e saída são iguais.",
        )

    chave = (ext_entrada.lstrip("."), formato_saida)
    if chave not in CONVERSOES_SUPORTADAS:
        raise HTTPException(
            status_code=400,
            detail=f"Conversão {ext_entrada} → .{formato_saida} não é suportada.",
        )

    filtro = CONVERSOES_SUPORTADAS[chave]

    tmpdir = tempfile.mkdtemp(prefix="fva_conv_")
    try:
        # Nome curto e seguro dentro do tmpdir
        entrada_path = os.path.join(
            tmpdir, f"entrada_{uuid.uuid4().hex}{ext_entrada}"
        )
        with open(entrada_path, "wb") as f:
            f.write(await file.read())

        nome_base = Path(nome_original).stem

        if filtro == "PDF2DOCX":
            saida_path = os.path.join(tmpdir, f"{nome_base}.docx")
            _converter_via_pdf2docx(entrada_path, saida_path)
            formato_final = "docx"
        else:
            soffice = _encontrar_soffice()
            _converter_via_libreoffice(soffice, entrada_path, tmpdir, filtro)
            formato_final = formato_saida
            saida_path = None
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

        # Nome de saída limpo
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
    return {
        "conversoes": [
            {"de": de, "para": para}
            for (de, para) in sorted(CONVERSOES_SUPORTADAS.keys())
        ]
    }