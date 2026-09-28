from pypdf import PdfReader


def extrair_texto_pdf(caminho_pdf: str) -> str:
    """Extrai texto de um PDF digital usando pypdf."""
    try:
        reader = PdfReader(caminho_pdf)
        partes = []
        for pagina in reader.pages:
            texto = pagina.extract_text()
            if texto:
                partes.append(texto)
        return "\n\n".join(partes).strip()
    except Exception as e:
        print(f"Erro ao extrair PDF com pypdf: {e}")
        return ""