import re
import unicodedata

ACENTOS_PT = (
    "áàâãäéèêëíìîïóòôõöúùûüçñýÿ"
    "ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑÝ"
)

CARACTERES_VALIDOS_RE = re.compile(
    r"[^\x09\x0A\x0D\x20-\x7E" + ACENTOS_PT + r"]"
)


def _e_titulo(linha: str) -> bool:
    """Detecta se a linha é um título (deve ficar em parágrafo próprio)."""
    s = linha.strip()
    if not s or len(s) > 100:
        return False

    # 1. "1 INTRODUÇÃO", "2.1. Contexto", "2.3 Objetivos"
    if re.match(r"^\d+(\.\d+)*\.?\s+\S", s):
        return True

    # 2. TUDO em MAIÚSCULAS (mas com pelo menos 3 letras)
    letras = [c for c in s if c.isalpha()]
    if letras and len(letras) >= 3:
        maiusculas = sum(1 for c in letras if c.isupper())
        if maiusculas / len(letras) > 0.9:
            return True

    # 3. Termina com ":" e é curto
    if s.endswith(":") and len(s) < 80:
        return True

    return False


def _reconstruir_paragrafos(texto: str) -> str:
    """
    Junta linhas quebradas em parágrafos REAIS,
    MAS preserva TÍTULOS como parágrafos separados.
    """
    linhas = texto.split("\n")
    resultado = []
    buffer = []

    def fechar_buffer():
        if buffer:
            resultado.append(" ".join(buffer))
            buffer.clear()

    for linha in linhas:
        stripped = linha.strip()

        if not stripped:
            fechar_buffer()
            continue

        if _e_titulo(stripped):
            fechar_buffer()
            resultado.append(stripped)
        else:
            buffer.append(stripped)

    fechar_buffer()

    return "\n\n".join(resultado)


def limpar_texto_bruto(texto: str) -> str:
    if not texto:
        return ""

    # 1. Normaliza Unicode
    texto = unicodedata.normalize("NFC", texto)

    # 2. Remove BOM e caracteres de controle
    texto = texto.replace("\ufeff", "")
    texto = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", texto)

    # 3. Remove qualquer caractere inválido (lixo ¡¢£¤¥...)
    texto = CARACTERES_VALIDOS_RE.sub("", texto)

    # 4. Normaliza quebras de linha
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")

    # 5. Colapsa espaços e tabs múltiplos
    texto = re.sub(r"[ \t]+", " ", texto)

    # 6. Junta linhas em parágrafos (preservando títulos)
    texto = _reconstruir_paragrafos(texto)

    # 7. Corrige espaços antes de pontuação
    texto = re.sub(r"\s+([,.;:!?])", r"\1", texto)

    # 8. Normaliza parágrafos (3+ quebras viram 2)
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()