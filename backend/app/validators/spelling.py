from spellchecker import SpellChecker

# Carrega o dicionário de Português
spell = SpellChecker(language='pt')


# ============================================================
# Whitelist: palavras acadêmicas/jurídicas que o dicionário
# pyspellchecker NÃO conhece e que seriam falso positivo.
# ============================================================
WHITELIST_ACADEMICA = {
    # Direito / Política
    "redemocratização", "democratização", "constitucionalização",
    "constitucionalismo", "constitucionalista", "inconstitucionalidade",
    "constitucionalidade", "jurisprudência", "jurisdicional", "jurisdicionais",
    "hermenêutica", "exegese", "exegético", "parlamentarismo",
    "presidencialismo", "parlamentarista", "pluripartidarismo",
    "bipartidarismo", "unipartidarismo", "oligarquização", "oligárquico",
    "oligárquica", "patrimonialismo", "patrimonialista", "coronelismo",
    "coronelista", "clientelismo", "clientelista", "populismo", "populista",
    "integralismo", "integralista", "tenentismo", "tenentista",
    "positivismo", "positivista", "republicanismo", "republicano",
    "republicana", "monarquismo", "monarquista", "abolicionismo",
    "abolicionista", "abolicionistas", "escravocratas", "escravagista",
    "proclamação", "promulgação", "promulgada", "promulgado",
    "outorgada", "outorgado", "emancipação", "alforria", "federação",
    "federativo", "federativa", "confederação", "legislativo", "executivo",
    "judiciário", "sufrágio", "sufragista", "censitário", "censitária",
    "mandonismo", "patronato", "kelseniana", "kelseniano",

    # Metodologia / Ciência
    "epistemologia", "epistemológico", "epistemológica", "metodologia",
    "metodológico", "metodológica", "bibliográfica", "bibliográfico",
    "documental", "qualitativo", "quantitativo", "qualitativa",
    "quantitativa", "exploratória", "descritiva", "explicativa",
    "hipótese", "hipóteses", "paradigma", "paradigmas", "paradigmático",
    "paradigmática", "empírico", "empírica", "empíricos", "axioma",
    "axiomas", "axiomático", "dialético", "dialética", "fenômeno",
    "fenômenos", "fenomenológico", "cognitivo", "cognitiva", "sistêmico",
    "sistêmica", "conjectura", "conjecturas", "corroboração", "corroborar",
    "hipoteticamente", "hipotético", "hipotética", "síntese", "sintético",
    "sintética", "diagnóstico", "prognóstico", "estatístico", "estatística",
    "amostragem", "amostral", "correlação", "variável", "variáveis",
    "pós-positivismo", "neopositivismo",

    # Conectivos acadêmicos
    "outrossim", "destarte", "porquanto", "conquanto", "entretanto",
    "contudo", "todavia", "outrora", "hodiernamente", "hodierno",
    "hodierna", "aludido", "aludida", "aludidos", "aludidas",
    "supracitado", "supracitada", "supramencionado", "supramencionada",
    "doravante", "consoante", "malgrado", "sobretudo",

    # História / Contexto
    "revolução", "revolucionário", "revolucionária", "revoluções",
    "revolucionários", "revolucionárias", "golpista", "golpismo",
    "ditadura", "ditatorial", "militarismo", "militarista", "militarização",
    "autoritarismo", "autoritário", "autoritária", "totalitarismo",
    "totalitário", "totalitária", "liberalismo", "liberais", "nacionalismo",
    "nacionalista", "comunismo", "comunista", "comunistas", "socialismo",
    "socialista", "socialistas", "capitalismo", "capitalista",
    "capitalistas", "anarquismo", "anarquista", "fascismo", "fascista",
    "nazismo", "nazista",

    # Economia / Sociedade
    "mercantilismo", "mercantilista", "industrialização", "industrializado",
    "industrializada", "urbanização", "urbanizado", "urbanizada",
    "modernização", "modernizado", "modernizada", "globalização",
    "globalizado", "globalizada", "desenvolvimentismo", "neoliberalismo",
    "neoliberal", "neoliberais", "keynesianismo", "keynesiano",
    "keynesiana", "socialdemocracia", "socialdemocrata", "ideologia",
    "ideológico", "ideológica", "hegemonia", "hegemônico", "hegemônica",
    "oligarquia", "oligarquias", "aristocracia", "aristocrático",
    "aristocrática", "meritocracia", "burocracia", "burocrático",
    "burocrática", "tecnocracia", "demagogia", "demagogo",

    # Verbos/termos comuns que o dicionário pode não pegar
    "vigente", "vigentes", "vigência", "prorrogado", "prorrogada",
    "prorrogação", "revogado", "revogada", "revogação", "sancionado",
    "sancionada", "sanção", "vetado", "vetada", "derrubado", "derrubada",
    "arquivado", "arquivada", "arquivamento", "suspenso", "suspensa",
    "suspensão", "dissolvido", "dissolvida", "dissolução", "decretado",
    "decretada", "decreto", "instaurado", "instaurada", "instauração",
    "expedido", "expedida", "expedição", "aprovado", "aprovada",
    "aprovação", "rejeitado", "rejeitada", "rejeição",
    "extinguiu", "extinguir", "extinção", "extinto", "aboliu", "abolir",
    "abolição", "promulgou", "outorgou", "decretou", "revogou",
    "sancionou", "vetou", "instituiu", "instituir", "instituição",
    "instituído", "instituída", "estabeleceu", "estabelecer",
    "consolidou", "consolidar", "consolidação", "configurou", "configurar",
    "configuração", "regulamentou", "regulamentar", "regulamentação",
    "reorganização", "reestruturação", "reconfiguração", "reeleição",
    "reeleger", "reeleito", "reabertura", "reabrir",
}

# ============================================================
# Informalidades: NÃO são erros ortográficos, são detectadas
# pelo grammar.py. Não devem aparecer na lista de Ortografia.
# ============================================================
INFORMALIDADES_IGNORAR = {
    "pra", "pro", "né", "tá", "vc", "pq", "qdo", "mt", "blz",
    "galera", "bagunça", "cara", "daí", "a", "gente", "meio",
    "tipo", "assim", "legal",
}

# Sufixos típicos de palavras acadêmicas longas
SUFIXOS_ACADEMICOS = (
    "ção", "ções", "mente", "ismo", "ismos", "ista", "istas",
    "ário", "ária", "ários", "árias",
    "ável", "áveis", "ível", "íveis",
    "oso", "osa", "osos", "osas",
    "ico", "ica", "icos", "icas",
    "ivo", "iva", "ivos", "ivas",
    "ência", "ências", "ância", "âncias",
)

# Sugestões que NUNCA devem aparecer (são lixo do dicionário)
BLACKLIST_SUGESTOES = {
    "pga", "pr", "nó", "ré", "ta", "va", "la",
    "oi", "eu", "tu", "ele", "ela", "vi", "vou",
    "pia", "pré", "pró", "na", "nê", "no",
}


def _e_palavra_academica(palavra: str) -> bool:
    """Detecta palavras que parecem acadêmicas/legítimas e não devem ser alertadas."""
    p = palavra.lower()

    if p in WHITELIST_ACADEMICA:
        return True

    if p in INFORMALIDADES_IGNORAR:
        return True

    # Palavras muito longas (12+ letras) geralmente são compostas corretas
    if len(p) >= 12:
        return True

    # Sufixo acadêmico + 8+ letras
    if len(p) >= 8 and p.endswith(SUFIXOS_ACADEMICOS):
        return True

    return False


def verificar_ortografia(texto: str):
    palavras = texto.split()
    palavras_limpas = [p.strip('.,;:!?()[]{}"\'-–—') for p in palavras]
    palavras_limpas = [p for p in palavras_limpas if p and p.isalpha()]

    palavras_para_checar = []
    for p in palavras_limpas:
        if p[0].isupper() and not p.isupper():
            continue
        if p.isupper():
            continue
        if _e_palavra_academica(p):
            continue
        palavras_para_checar.append(p)

    vistos = set()
    palavras_unicas = []
    for p in palavras_para_checar:
        if p.lower() not in vistos:
            vistos.add(p.lower())
            palavras_unicas.append(p)

    palavras_erradas = spell.unknown(palavras_unicas)

    erros = []
    for palavra in palavras_erradas:
        sugestoes_raw = spell.candidates(palavra) or set()

        sugestoes_boas = [
            s for s in sugestoes_raw
            if s.lower() not in BLACKLIST_SUGESTOES
            and abs(len(s) - len(palavra)) <= 3
            and s[0].lower() == palavra[0].lower()
        ]

        if not sugestoes_boas:
            continue

        erros.append({
            "palavra": palavra,
            "sugestoes": sorted(sugestoes_boas, key=len)[:3],
        })

    return erros