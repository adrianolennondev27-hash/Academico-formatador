from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import tempfile

from app.converters.pdf_extractor import extrair_texto_pdf
from app.ocr.engine import extrair_texto_ocr
from app.core.text_cleaner import limpar_texto_bruto

router = APIRouter(prefix="/api/v1", tags=["upload"])

@router.post("/upload")
async def upload_arquivo(file: UploadFile = File(...)):
    # Verifica se é PDF (por enquanto, vamos focar em PDF)
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Por enquanto, apenas arquivos PDF são aceitos.")

    # Salva o arquivo temporariamente para processamento
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        caminho_temporario = temp_file.name

    try:
        # 1. Tenta extração direta
        texto_bruto = extrair_texto_pdf(caminho_temporario)
        
        # 2. Se o texto for muito curto (provavelmente PDF escaneado), aciona OCR
        if len(texto_bruto) < 50:
            print("PDF parece ser escaneado. Acionando OCR...")
            texto_bruto = extrair_texto_ocr(caminho_temporario)
            
        if not texto_bruto:
            raise HTTPException(status_code=422, detail="Não foi possível extrair texto do PDF.")

        # 3. Limpa o texto usando o módulo que criamos anteriormente
        texto_limpo = limpar_texto_bruto(texto_bruto)

        return {
            "nome_arquivo": file.filename,
            "texto_extraido": texto_limpo,
            "metodo": "OCR" if len(texto_bruto) > 50 and len(extrair_texto_pdf(caminho_temporario)) < 50 else "Digital"
        }

    finally:
        # Remove o arquivo temporário (Garantia de Privacidade/Stateless)
        if os.path.exists(caminho_temporario):
            os.remove(caminho_temporario)