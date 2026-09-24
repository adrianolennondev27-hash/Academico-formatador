import pdfplumber

def extrair_texto_pdf(caminho_pdf: str) -> str:
    """Tenta extrair texto de um PDF digital."""
    texto = ""
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            for pagina in pdf.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto += texto_pagina + "\n\n"
    except Exception as e:
        print(f"Erro ao extrair PDF: {e}")
        return ""
    return texto.strip()