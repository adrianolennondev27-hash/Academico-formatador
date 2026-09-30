from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from io import BytesIO
import re
import unicodedata


SEPARADORES_NOMES_RE = re.compile(
    r"[\u002C\u003B\u060C\u061B\u201A\u201B\u3001\uFF0C\uFF1B]+"
)

PADRAO_INICIO_REFERENCIA = re.compile(
    r"(?<![A-ZÁÉÍÓÚÂÊÔÃÕÇ])"
    r"([A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,}(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,})?)\s*,\s*"
    r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ]\.?"
)


def _configurar_margens(secao):
    secao.top_margin = Cm(3)
    secao.left_margin = Cm(3)
    secao.bottom_margin = Cm(2)
    secao.right_margin = Cm(2)


def _limpar_footer(secao):
    secao.footer.is_linked_to_previous = False
    for p in list(secao.footer.paragraphs):
        p._element.getparent().remove(p._element)
    secao.footer.add_paragraph()


def _cidade_ano_no_footer(secao, cidade: str, ano: str):
    _limpar_footer(secao)
    footer = secao.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if cidade:
        run = p.add_run(cidade)
        run.font.name = 'Arial'
        run.font.size = Pt(12)

    if ano:
        p_ano = footer.add_paragraph()
        p_ano.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p_ano.add_run(ano)
        run.font.name = 'Arial'
        run.font.size = Pt(12)


def _limpar_footer_secao(secao):
    secao.footer.is_linked_to_previous = False
    for p in list(secao.footer.paragraphs):
        p._element.getparent().remove(p._element)
    secao.footer.add_paragraph()


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


def _separar_referencias(texto: str) -> list:
    if not texto.strip():
        return []

    texto = texto.replace("\t", " ")
    linhas = [l.strip() for l in re.split(r"\n+", texto) if l.strip()]

    if len(linhas) < 2:
        texto_unico = texto.strip()
        partes = re.split(r"\s{2,}", texto_unico)
        partes = [p.strip() for p in partes if p.strip()]
        if len(partes) >= 2:
            linhas = partes

    if len(linhas) < 2:
        texto_unico = linhas[0] if linhas else texto.strip()
        matches = list(PADRAO_INICIO_REFERENCIA.finditer(texto_unico))
        if len(matches) >= 2:
            novas = []
            for i, m in enumerate(matches):
                inicio = m.start()
                fim = matches[i + 1].start() if i + 1 < len(matches) else len(texto_unico)
                ref = texto_unico[inicio:fim].strip()
                if ref:
                    novas.append(ref)
            linhas = novas

    resultado = []
    for linha in linhas:
        linha = re.sub(r"\s+", " ", linha).strip()
        linha = re.sub(r"\s+([,.;:!?])", r"\1", linha)
        if linha:
            resultado.append(linha)

    return resultado


def _adicionar_pagina_referencias(doc, referencias_texto: str):
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("REFERÊNCIAS")
    run.bold = True
    run.font.size = Pt(12)

    referencias = _separar_referencias(referencias_texto)

    for ref in referencias:
        p = doc.add_paragraph(ref)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.first_line_indent = Cm(0)


def _separar_nomes(alunos_raw: str) -> list:
    if not alunos_raw:
        return []
    alunos_raw = unicodedata.normalize("NFC", alunos_raw)
    alunos_raw = alunos_raw.strip()
    alunos_raw = re.sub(r"[\t\n\r]+", " ", alunos_raw)
    alunos_raw = re.sub(r"\s+", " ", alunos_raw).strip()

    if SEPARADORES_NOMES_RE.search(alunos_raw):
        partes = SEPARADORES_NOMES_RE.split(alunos_raw)
        return [p.strip() for p in partes if p.strip()]

    nomes = re.findall(
        r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+"
        r"(?:\s+(?:da|de|do|das|dos|e)\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+"
        r"|\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)*",
        alunos_raw,
    )
    nomes = [n.strip() for n in nomes if len(n.strip()) > 3]
    if len(nomes) >= 2:
        return nomes
    return [alunos_raw]


def _detectar_titulo(paragrafo: str) -> tuple:
    match = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(.+)$", paragrafo.strip())
    if match:
        numero = match.group(1)
        titulo = match.group(2).strip()
        if titulo and len(titulo) < 120:
            return numero, titulo
    return None, None


def _criar_sumario(doc, titulos: list):
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
    # Só cria a página de REFERÊNCIAS se o checkbox estiver marcado E tiver texto
    tem_referencias = bool(
        metadados.get("incluir_referencias")
        and metadados.get("referencias", "").strip()
    )

    cidade = metadados.get("cidade", "")
    ano = metadados.get("ano", "")

    # SEÇÃO 1: CAPA
    secao_1 = doc.sections[0]
    _configurar_margens(secao_1)
    secao_1.different_first_page_header_footer = True
    _cidade_ano_no_footer(secao_1, cidade, ano)

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
    p.paragraph_format.space_before = Pt(140)

    # SEÇÃO 2: FOLHA DE ROSTO
    if tem_folha_rosto:
        secao_2 = doc.add_section(WD_SECTION.NEW_PAGE)
        _configurar_margens(secao_2)
        secao_2.different_first_page_header_footer = True
        _cidade_ano_no_footer(secao_2, cidade, ano)

        primeiro = True
        for nome in lista_alunos:
            p = doc.add_paragraph(nome)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if primeiro:
                p.paragraph_format.space_before = Pt(20)
                primeiro = False

        p = doc.add_paragraph(metadados.get("titulo", "").upper())
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].bold = True
        p.paragraph_format.space_before = Pt(40)

        p = doc.add_paragraph(metadados.get("natureza_trabalho", ""))
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(8)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(30)

    # SEÇÃO 3: SUMÁRIO
    if tem_sumario:
        secao_sumario = doc.add_section(WD_SECTION.NEW_PAGE)
        _configurar_margens(secao_sumario)
        secao_sumario.different_first_page_header_footer = True
        _limpar_footer_secao(secao_sumario)
        _criar_sumario(doc, titulos_detectados)

    # SEÇÃO FINAL: TEXTO
    secao_texto = doc.add_section(WD_SECTION.NEW_PAGE)
    _configurar_margens(secao_texto)
    _limpar_footer_secao(secao_texto)
    _adicionar_numeracao_paginas(secao_texto, start_num=3)

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

    # Só adiciona REFERÊNCIAS se o checkbox estiver marcado E tiver texto
    if tem_referencias:
        _adicionar_pagina_referencias(doc, metadados.get("referencias", ""))

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer