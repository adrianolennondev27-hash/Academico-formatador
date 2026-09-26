from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import tempfile
import zipfile

from app.converters.pdf_extractor import extrair_texto_pdf
from app.ocr.engine import extrair_texto_ocr
from app.core.text_cleaner import limpar_texto_bruto

router = APIRouter(prefix="/api/v1", tags=["upload"])


def _e_docx_real(caminho: str) -> bool:
    """Verifica se o arquivo é um .docx de verdade (ZIP contendo word/document.xml)."""
    try:
        with zipfile.ZipFile(caminho, "r") as z:
            nomes = z.namelist()
            return any(n.startswith("word/document") for n in nomes)
    except Exception:
        return False


def _extrair_texto_docx(caminho: str) -> str:
    """Extrai o texto de um arquivo .docx usando python-docx."""
    try:
        from docx import Document
        doc = Document(caminho)
        paragrafos = []
        for p in doc.paragraphs:
            t = p.text.strip()
            if t:
                paragrafos.append(t)
        return "\n\n".join(paragrafos)
    except Exception as e:
        print(f"Erro ao extrair DOCX: {e}")
        return ""


def _extrair_texto_txt(caminho: str) -> str:
    """Lê um arquivo .txt tentando UTF-8 e caindo para latin-1."""
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(caminho, "r", encoding="latin-1") as f:
            return f.read()
    except Exception as e:
        print(f"Erro ao extrair TXT: {e}")
        return ""


@router.post("/upload")
async def upload_arquivo(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    nome = file.filename.lower()
    ext = os.path.splitext(nome)[1]

    EXTENSOES_ACEITAS = {".pdf", ".docx", ".txt"}
    if ext not in EXTENSOES_ACEITAS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Formato '{ext}' não aceito. "
                "Envie PDF, DOCX (Word 2007+) ou TXT. "
                "Se o seu arquivo é .doc (Word antigo), salve como .docx antes."
            ),
        )

    # Salva o arquivo temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        caminho_temporario = temp_file.name

    try:
        texto_bruto = ""
        metodo = "Digital"

        # ---------------------------------------------
        # PDF
        # ---------------------------------------------
        if ext == ".pdf":
            texto_bruto = extrair_texto_pdf(caminho_temporario)

            # Se texto curto → provavelmente escaneado → OCR
            if len(texto_bruto) < 50:
                print("PDF parece ser escaneado. Acionando OCR...")
                texto_bruto = extrair_texto_ocr(caminho_temporario)
                metodo = "OCR"

            if not texto_bruto:
                raise HTTPException(
                    status_code=422,
                    detail="Não foi possível extrair texto do PDF.",
                )

        # ---------------------------------------------
        # DOCX (Word 2007+)
        # ---------------------------------------------
        elif ext == ".docx":
            if not _e_docx_real(caminho_temporario):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "O arquivo tem extensão .docx, mas não é um documento Word válido. "
                        "Verifique se não é um PDF renomeado ou um arquivo corrompido."
                    ),
                )
            texto_bruto = _extrair_texto_docx(caminho_temporario)
            metodo = "Word (DOCX)"
            if not texto_bruto:
                raise HTTPException(
                    status_code=422,
                    detail="Não foi possível extrair texto do documento Word.",
                )

        # ---------------------------------------------
        # TXT
        # ---------------------------------------------
        elif ext == ".txt":
            texto_bruto = _extrair_texto_txt(caminho_temporario)
            metodo = "Texto (TXT)"
            if not texto_bruto.strip():
                raise HTTPException(
                    status_code=422,
                    detail="O arquivo de texto está vazio.",
                )

        # Limpa o texto
        texto_limpo = limpar_texto_bruto(texto_bruto)

        return {
            "nome_arquivo": file.filename,
            "texto_extraido": texto_limpo,
            "metodo": metodo,
        }

    finally:
        if os.path.exists(caminho_temporario):
            os.remove(caminho_temporario)