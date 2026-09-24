import os
import shutil
import subprocess
import tempfile
from io import BytesIO

from fastapi import HTTPException


def _encontrar_soffice() -> str:
    caminho = shutil.which("soffice") or shutil.which("libreoffice")
    if caminho:
        return caminho

    candidatos = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c

    raise HTTPException(
        status_code=500,
        detail="LibreOffice não encontrado. Instale com: winget install TheDocumentFoundation.LibreOffice",
    )


def converter_docx_para_pdf(buffer_docx: BytesIO) -> BytesIO:
    soffice = _encontrar_soffice()

    with tempfile.TemporaryDirectory() as tmpdir:
        docx_path = os.path.join(tmpdir, "documento.docx")
        pdf_path = os.path.join(tmpdir, "documento.pdf")

        with open(docx_path, "wb") as f:
            f.write(buffer_docx.getvalue())

        try:
            subprocess.run(
                [soffice, "--headless", "--convert-to", "pdf", "--outdir", tmpdir, docx_path],
                check=True,
                timeout=90,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Falha na conversão: {e.stderr.decode(errors='ignore')}",
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=500, detail="Timeout na conversão.")

        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="PDF não foi gerado.")

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

    buffer_pdf = BytesIO(pdf_bytes)
    buffer_pdf.seek(0)
    return buffer_pdf