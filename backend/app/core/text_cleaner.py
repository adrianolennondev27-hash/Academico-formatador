import re
import unicodedata


# ============================================================
# Whitelist EXATA — só o que é permitido em texto português
# ============================================================
ACENTOS_PT = (
    "áàâãäéèêëíìîïóòôõöúùûüçñýÿ"
    "ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑÝ"
)

CARACTERES_VALIDOS_RE = re.compile(
    r"[^\x09\x0A\x0D\x20-\x7E" + ACENTOS_PT + r"]"
)

LIXO_UNICODE_RE = re.compile(
    r"[\u00A0-\u00BF"
    r"\u00C5\u00C6"
    r"\u00D0\u00D7\u00D8"
    r"\u00DD\u00DE\u00DF"
    r"\u00E5\u00E6"
    r"\u00F0\u00F7\u00F8"
    r"\u00FD\u00FE\u00FF]"
)


def _remover_invisiveis(texto: str) -> str:
    """
    Remove TODOS os caracteres invisíveis do texto.

    Isso inclui:
    - Cf (Format): zero-width space, zero-width joiner, BOM, soft hyphen,
      directional marks, word joiner, etc.
    - Cc (Control): exceto \\t, \\n, \\r
    - Cs (Surrogate), Co (Private Use), Cn (Unassigned)
    - Zl, Zp (Line/Paragraph Separator) — raramente usados

    Esses caracteres NÃO aparecem visualmente no Word, mas estão no arquivo.
    Detectores de IA e sistemas de auditoria os encontram.
    """
    resultado = []
    for c in texto:
        cat = unicodedata.category(c)

        # Mantém tab, newline e carriage return
        if c in ("\t", "\n", "\r"):
            resultado.append(c)
            continue

        # Remove tudo que é Cf (Format), Cc (Control), Cs, Co, Cn
        if cat in ("Cf", "Cc", "Cs", "Co", "Cn"):
            continue

        # Remove Zl e Zp (line/paragraph separator)
        if cat in ("Zl", "Zp"):
            resultado.append("\n")
            continue

        resultado.append(c)

    return "".join(resultado)


def _lixeira_final(texto: str) -> str:
    """Última passada — remove lixo residual visível."""
    texto = LIXO_UNICODE_RE.sub(" ", texto)
    texto = re.sub(r"(?:[^\x00-\x7F]+\s*){5,}", " ", texto)
    texto = CARACTERES_VALIDOS_RE.sub("", texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\s+([,.;:!?])", r"\1", texto)

    linhas = [l.strip() for l in texto.split("\n")]
    texto = "\n".join(linhas)
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()


def _reconstruir_paragrafos(texto: str) -> str:
    """Junta linhas quebradas em parágrafos REAIS, preservando títulos."""
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

        if re.match(r"^\d+(\.\d+)*\.?\s+\S", stripped):
            fechar_buffer()
            resultado.append(stripped)
            continue

        letras = [c for c in stripped if c.isalpha()]
        if letras and len(letras) >= 3:
            maiusculas = sum(1 for c in letras if c.isupper())
            if maiusculas / len(letras) > 0.9:
                fechar_buffer()
                resultado.append(stripped)
                continue

        buffer.append(stripped)

    fechar_buffer()
    return "\n\n".join(resultado)


def limpar_texto_bruto(texto: str) -> str:
    """
    Limpeza em 4 etapas:
    1. Normalização Unicode + remoção de control chars
    2. Remoção de caracteres INVISÍVEIS (Cf, Cc, Cs, Co, Cn, Zl, Zp)
    3. Remoção de lixo visível (símbolos estranhos)
    4. Reconstrução de parágrafos
    """
    if not texto:
        return ""

    # 1. Normaliza Unicode
    texto = unicodedata.normalize("NFC", texto)
    texto = texto.replace("\ufeff", "")
    texto = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", texto)

    # 2. Normaliza quebras de linha
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")

    # 3. REMOVE INVISÍVEIS (a etapa que faltava)
    texto = _remover_invisiveis(texto)

    # 4. Colapsa espaços/tabs múltiplos
    texto = re.sub(r"[ \t]+", " ", texto)

    # 5. LIXEIRA FINAL — remove lixo residual visível
    texto = _lixeira_final(texto)

    # 6. Reconstroi parágrafos
    texto = _reconstruir_paragrafos(texto)

    return texto.strip()