from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from io import BytesIO
import re
import unicodedata


# ============================================================
# Separadores de nomes — aceita QUALQUER tipo de vírgula:
#   U+002C  ,   vírgula ASCII comum (teclado PT-BR)
#   U+003B  ;   ponto-e-vírgula ASCII
#   U+060C  ،   vírgula árabe
#   U+061B  ؛   ponto-e-vírgula árabe
#   U+201A  ‚   vírgula baixa (smart quote)
#   U+201B  ‛   aspas simples alta invertida
#   U+3001  、   vírgula ideográfica CJK
#   U+FF0C  ，   vírgula fullwidth (chinês/japonês)
#   U+FF1B  ；   ponto-e-vírgula fullwidth
# ============================================================
SEPARADORES_NOMES_RE = re.compile(
    r"[\u002C\u003B\u060C\u061B\u201A\u201B\u3001\uFF0C\uFF1B]+"
)


def _configurar_margens(secao):
    secao.top_margin = Cm(3)
    secao.left_margin = Cm(3)
    secao.bottom_margin = Cm(2)
    secao.right_margin = Cm(2)


def _adicionar_numeracao_paginas(secao, start_num=3):
    header = secao.header
    header.is_linked_to_previous = False
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run()

    fld_begin = OxmlElement('w:fldChar')
    fld_begin.set(qn('w:fldCharType'), 'begin')
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = 'PAGE'
    fld_end = OxmlElement('w:fldChar')
    fld_end.set(qn('w:fldCharType'), 'end')

    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)

    sectPr = secao._sectPr
    pgNumType = OxmlElement('w:pgNumType')
    pgNumType.set(qn('w:start'), str(start_num))
    sectPr.append(pgNumType)


def _adicionar_pagina_referencias(doc):
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("REFERÊNCIAS")
    run.bold = True
    run.font.size = Pt(12)


def _separar_nomes(alunos_raw: str) -> list:
    """
    Separa nomes de autores em lista.
    Aceita TODOS os tipos de vírgula conhecidos (ASCII, árabe, fullwidth, CJK).
    """
    if not alunos_raw:
        return []

    # Normaliza Unicode (resolve vírgulas "diferentes" e caracteres compostos)
    alunos_raw = unicodedata.normalize("NFC", alunos_raw)

    # Limpa tabs, quebras e espaços múltiplos
    alunos_raw = alunos_raw.strip()
    alunos_raw = re.sub(r"[\t\n\r]+", " ", alunos_raw)
    alunos_raw = re.sub(r"\s+", " ", alunos_raw).strip()

    # Se tem QUALQUER tipo de vírgula, separa
    if SEPARADORES_NOMES_RE.search(alunos_raw):
        partes = SEPARADORES_NOMES_RE.split(alunos_raw)
        return [p.strip() for p in partes if p.strip()]

    # Fallback: tenta detectar nomes próprios por padrão (Maiúscula + minúsculas)
    nomes = re.findall(
        r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+"
        r"(?:\s+(?:da|de|do|das|dos|e)\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+"
        r"|\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)*",
        alunos_raw,
    )
    nomes = [n.strip() for n in nomes if len(n.strip()) > 3]
    if len(nomes) >= 2:
        return nomes

    # Último recurso: retorna o texto inteiro como 1 nome
    return [alunos_raw]


def _detectar_titulo(paragrafo: str) -> tuple:
    """
    Detecta se um parágrafo é um título numerado.
    Retorna (numero, titulo_sem_numero) ou (None, None).
    Ex: '1. INTRODUÇÃO' → ('1', 'INTRODUÇÃO')
        '2.1. Contexto' → ('2.1', 'Contexto')
    """
    match = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(.+)$", paragrafo.strip())
    if match:
        numero = match.group(1)
        titulo = match.group(2).strip()
        if titulo and len(titulo) < 120:
            return numero, titulo
    return None, None


def _criar_sumario(doc, titulos: list):
    """Cria página de sumário com os títulos detectados."""
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("SUMÁRIO")
    run.bold = True
    run.font.size = Pt(12)

    doc.add_paragraph()

    for numero, titulo in titulos:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.5
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT

        nivel = numero.count(".")
        if nivel == 0:
            p.paragraph_format.left_indent = Cm(0)
        elif nivel == 1:
            p.paragraph_format.left_indent = Cm(0.75)
        else:
            p.paragraph_format.left_indent = Cm(1.5)

        texto_sumario = f"{numero} {titulo.upper()}"
        run = p.add_run(texto_sumario)
        run.font.size = Pt(12)
        if nivel == 0:
            run.bold = True


def gerar_documento_abnt(metadados: dict, texto: str) -> BytesIO:
    doc = Document()

    estilo = doc.styles['Normal']
    estilo.font.name = 'Arial'
    estilo.font.size = Pt(12)
    estilo.paragraph_format.line_spacing = 1.5
    estilo.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    estilo.paragraph_format.space_after = Pt(0)

    lista_alunos = _separar_nomes(metadados.get("aluno", ""))

    # Pré-processa texto: separa parágrafos e detecta títulos
    paragrafos = [p.strip() for p in texto.split('\n\n') if p.strip()]
    titulos_detectados = []
    for par in paragrafos:
        num, tit = _detectar_titulo(par)
        if num:
            titulos_detectados.append((num, tit))

    tem_folha_rosto = bool(
        metadados.get("incluir_folha_rosto")
        and metadados.get("natureza_trabalho")
    )
    tem_sumario = bool(
        metadados.get("incluir_sumario")
        and titulos_detectados
    )

    secao_1 = doc.sections[0]
    _configurar_margens(secao_1)
    secao_1.different_first_page_header_footer = True

    # ============================================
    # CAPA
    # ============================================
    def criar_capa():
        p = doc.add_paragraph(metadados.get("instituicao", "").upper())
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p = doc.add_paragraph(metadados.get("curso", ""))
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        primeiro = True
        for nome in lista_alunos:
            p = doc.add_paragraph(nome)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if primeiro:
                p.paragraph_format.space_before = Pt(100)
                primeiro = False

        p = doc.add_paragraph(metadados.get("titulo", "").upper())
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].bold = True
        p.paragraph_format.space_before = Pt(100)

        p = doc.add_paragraph(metadados.get("cidade", ""))
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(220)

        p = doc.add_paragraph(metadados.get("ano", ""))
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    criar_capa()

    # ============================================
    # FOLHA DE ROSTO
    # ============================================
    def criar_folha_rosto():
        primeiro = True
        for nome in lista_alunos:
            p = doc.add_paragraph(nome)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if primeiro:
                p.paragraph_format.page_break_before = True
                p.paragraph_format.space_before = Pt(60)
                primeiro = False

        p = doc.add_paragraph(metadados.get("titulo", "").upper())
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].bold = True
        p.paragraph_format.space_before = Pt(100)

        p = doc.add_paragraph(metadados.get("natureza_trabalho", ""))
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(8)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(100)

        p = doc.add_paragraph(metadados.get("cidade", ""))
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(200)

        p = doc.add_paragraph(metadados.get("ano", ""))
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if tem_folha_rosto:
        secao_2 = doc.add_section(WD_SECTION.NEW_PAGE)
        _configurar_margens(secao_2)
        secao_2.different_first_page_header_footer = True
        criar_folha_rosto()

    # ============================================
    # SUMÁRIO
    # ============================================
    if tem_sumario:
        if tem_folha_rosto:
            _criar_sumario(doc, titulos_detectados)
        else:
            secao_sumario = doc.add_section(WD_SECTION.NEW_PAGE)
            _configurar_margens(secao_sumario)
            secao_sumario.different_first_page_header_footer = True
            _criar_sumario(doc, titulos_detectados)

    # ============================================
    # TEXTO (com numeração de páginas)
    # ============================================
    secao_3 = doc.add_section(WD_SECTION.NEW_PAGE)
    _configurar_margens(secao_3)
    _adicionar_numeracao_paginas(secao_3, start_num=3)

    for par in paragrafos:
        num, tit = _detectar_titulo(par)

        if num:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.space_before = Pt(12)
            run = p.add_run(f"{num} {tit.upper()}")
            run.bold = True
        else:
            p = doc.add_paragraph(par)
            p.paragraph_format.first_line_indent = Cm(1.25)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.space_after = Pt(0)

    _adicionar_pagina_referencias(doc)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer