import re
import unicodedata

# ============================================================
# Todos os caracteres usam ESCAPES UNICODE (\u00e1 = á)
# Assim o arquivo é 100% ASCII e não pode ser corrompido.
# ============================================================

_PT_LOWER = (
    "\u00e1\u00e0\u00e2\u00e3\u00e4"
    "\u00e9\u00e8\u00ea\u00eb"
    "\u00ed\u00ec\u00ee\u00ef"
    "\u00f3\u00f2\u00f4\u00f5\u00f6"
    "\u00fa\u00f9\u00fb\u00fc"
    "\u00e7\u00f1"
)
_PT_UPPER = (
    "\u00c1\u00c0\u00c2\u00c3\u00c4"
    "\u00c9\u00c8\u00ca\u00cb"
    "\u00cd\u00cc\u00ce\u00cf"
    "\u00d3\u00d2\u00d4\u00d5\u00d6"
    "\u00da\u00d9\u00db\u00dc"
    "\u00c7\u00d1"
)
ACENTOS_VALIDOS = _PT_LOWER + _PT_UPPER

BULLET = "\u2022"        # •
CHECKBOX = "\u2610"      # ☐
UPPER_ACCENTED = _PT_UPPER


def _remover_lixo(texto: str) -> str:
    # 1. Protege APENAS os marcadores de bullet confiáveis (• e ☐)
    #    Não protege '·' (MIDDLE_DOT) porque é comum no meio de textos
    #    e causa falsos positivos como "a)".
    texto = texto.replace(BULLET, "[[BUL]]")
    texto = texto.replace(CHECKBOX, "[[BUL]]")

    # 2. Whitelist: mantém só ASCII imprimível + acentos PT + colchetes
    chars_ok = "\x09\x0A\x0D\x20-\x7E" + ACENTOS_VALIDOS + r"\[\]"
    texto = re.sub(rf"[^{chars_ok}]", "", texto)

    # 3. Remove sequências de 5+ não-ASCII (com espaços opcionais)
    #    Nenhum texto em português tem 5 acentos seguidos.
    texto = re.sub(r"(?:[^\x00-\x7F]\s*){5,}", " ", texto)

    # 4. Restaura marcadores
    texto = texto.replace("[[BUL]]", BULLET)

    return texto


def _converter_alineas(texto: str) -> str:
    linhas = texto.split("\n")
    resultado = []
    contador = 0

    for linha in linhas:
        # Preserva linhas vazias sem mexer no contador
        if not linha.strip():
            resultado.append(linha)
            continue

        stripped = linha.strip()

        # Marcador bullet confiável (•, ☐, *, -) seguido de conteúdo
        # (removido o '·' que causava falsos positivos)
        match_bullet = re.match(
            rf"^[\u2022\u2610\*\-]\s+(.+)$", stripped
        )
        if match_bullet:
            letra = chr(ord('a') + (contador % 26))
            contador += 1
            resultado.append("")
            resultado.append(f"{letra}) {match_bullet.group(1)}")
            resultado.append("")
            continue

        # Marcador "o " + Maiúscula + ":" (ex: "o Voto Feminino:")
        match_o = re.match(
            rf"^[oO]\s+([A-Z{UPPER_ACCENTED}].+?):", stripped
        )
        if match_o:
            letra = chr(ord('a') + (contador % 26))
            contador += 1
            resultado.append("")
            resultado.append(f"{letra}) {stripped[2:]}")
            resultado.append("")
            continue

        resultado.append(linha)

    return "\n".join(resultado)


def limpar_texto_bruto(texto: str) -> str:
    if not texto:
        return ""

    texto = unicodedata.normalize("NFC", texto)
    texto = texto.replace("\ufeff", "")
    texto = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", texto)

    texto = _remover_lixo(texto)

    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    texto = re.sub(r"(\w)-\n(\w)", r"\1\2", texto)

    texto = _converter_alineas(texto)

    texto = re.sub(r"\n\s*\d{1,4}\s*\n", "\n\n", texto)

    texto = re.sub(r"\n{2,}", "[[Q]]", texto)
    texto = re.sub(r"\n", " ", texto)
    texto = texto.replace("[[Q]]", "\n\n")

    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\s+([,.;:!?])", r"\1", texto)
    texto = re.sub(r"([,.;:!?])(?=[A-Za-z\u00c0-\u00ff])", r"\1 ", texto)

    paragrafos = [p.strip() for p in texto.split('\n\n') if p.strip()]
    texto = '\n\n'.join(paragrafos)

    if texto.count('\n\n') < 5 and len(texto) > 1000:
        texto = re.sub(
            rf'(?<=[.!?])\s+(?=[A-Z{UPPER_ACCENTED}])', '\n\n', texto
        )

    return texto.strip()