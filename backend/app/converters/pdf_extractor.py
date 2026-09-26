import pdfplumber


def extrair_texto_pdf(caminho_pdf: str) -> str:
    """Extrai texto de um PDF digital. Retorna string vazia se falhar."""
    texto = ""
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            for pagina in pdf.pages:
                try:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto += texto_pagina + "\n\n"
                except Exception as e:
                    print(f"Erro ao extrair página: {e}")
                    continue
    except Exception as e:
        print(f"Erro ao abrir PDF: {e}")
        return ""
    return texto.strip()