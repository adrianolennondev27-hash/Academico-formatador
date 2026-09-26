import re


# ============================================================
# Informalidades e abreviações que devem ser evitadas em textos
# acadêmicos. Chave = regex, valor = (palavra_mostrada, dica)
# ============================================================
INFORMALIDADES = {
    r"\btipo assim\b": ("tipo assim", "Evite a expressão 'tipo assim' em textos acadêmicos."),
    r"\bné\b": ("né", "Evite a abreviação 'né' (use 'não é')."),
    r"\bpra\b": ("pra", "Evite a forma reduzida 'pra' (use 'para')."),
    r"\bpro\b": ("pro", "Evite a forma reduzida 'pro' (use 'para o')."),
    r"\btá\b": ("tá", "Evite a forma reduzida 'tá' (use 'está')."),
    r"\bvc\b": ("vc", "Evite a abreviação 'vc' (use 'você')."),
    r"\bpq\b": ("pq", "Evite a abreviação 'pq' (use 'porque')."),
    r"\bqdo\b": ("qdo", "Evite a abreviação 'qdo' (use 'quando')."),
    r"\bmt\b": ("mt", "Evite a abreviação 'mt' (use 'muito')."),
    r"\bblz\b": ("blz", "Evite a abreviação 'blz' em textos acadêmicos."),
    r"\ba gente\b": ("a gente", "Em textos acadêmicos, prefira 'nós' em vez de 'a gente'."),
    r"\bmeio que\b": ("meio que", "Evite a expressão 'meio que' em textos formais."),
    r"\bmuito legal\b": ("muito legal", "Evite 'muito legal' em textos acadêmicos."),
    r"\bbem legal\b": ("bem legal", "Evite 'bem legal' em textos acadêmicos."),
    r"\bdaí\b": ("daí", "Evite o termo 'daí' em textos acadêmicos."),
    r"\bgalera\b": ("galera", "Evite 'galera' em textos acadêmicos."),
    r"\bbagunça\b": ("bagunça", "Evite 'bagunça' em textos acadêmicos."),
    r"\bcara\b": ("cara", "Evite o termo 'cara' em textos acadêmicos."),
}

# Pronomes/verbos em 1ª pessoa (evitar em textos acadêmicos)
PRIMEIRA_PESSOA_PADROES = [
    r"\beu\b", r"\bnós\b",
    r"\bmeu\b", r"\bminha\b", r"\bmeus\b", r"\bminhas\b",
    r"\bnosso\b", r"\bnossa\b", r"\bnossos\b", r"\bnossas\b",
    r"\bacho\b", r"\bachamos\b",
    r"\bpenso\b", r"\bpensamos\b",
    r"\bvejo\b", r"\bvemos\b",
    r"\bobservo\b", r"\bobservamos\b",
    r"\bconsidero\b", r"\bconsideramos\b",
    r"\bavalio\b", r"\bavaliamos\b",
    r"\bcreio\b", r"\bcremos\b",
    r"\bentendo\b", r"\bentendemos\b",
    r"\bpercebo\b", r"\bpercebemos\b",
    r"\bacredito\b", r"\bacreditamos\b",
]


def verificar_gramatica(texto: str):
    erros = []
    texto_lower = texto.lower()

    # 1. "a" no lugar de "há" (tempo decorrido)
    padrao_a_ha = re.compile(
        r"\ba\s+(?:\w+\s+)*(?:dias?|meses?|anos?|horas?|minutos?|semanas?|décadas?)\b",
        re.IGNORECASE,
    )
    for match in padrao_a_ha.finditer(texto):
        erros.append({
            "tipo": "gramatica",
            "regra": "Uso de 'a' no lugar de 'há'",
            "trecho": match.group(0),
            "dica": "Você quis dizer 'há'? (Ex: 'há dois anos' indica tempo passado)",
        })

    # 2. "mais" no lugar de "mas"
    padrao_mais_mas = re.compile(
        r"\bmais\b(?=\s+(não|sim|é|foi|está|era|será|o|a|os|as)\b)",
        re.IGNORECASE,
    )
    for match in padrao_mais_mas.finditer(texto):
        erros.append({
            "tipo": "gramatica",
            "regra": "Possível uso incorreto de 'mais' (em vez de 'mas')",
            "trecho": match.group(0),
            "dica": "Verifique se o correto seria 'mas' (conjunção adversativa).",
        })

    # 3. Espaço antes de pontuação
    padrao_espaco_pontuacao = re.compile(r"\s+([,.;:!?])")
    for match in padrao_espaco_pontuacao.finditer(texto):
        erros.append({
            "tipo": "pontuacao",
            "regra": "Espaço antes de pontuação",
            "trecho": match.group(0),
            "dica": "Remova o espaço antes da pontuação.",
        })

    # 4. Falta de espaço depois de pontuação
    padrao_falta_espaco = re.compile(r"([,.;:!?])(?=[A-Za-zÀ-ÿ])")
    for match in padrao_falta_espaco.finditer(texto):
        erros.append({
            "tipo": "pontuacao",
            "regra": "Falta de espaço após pontuação",
            "trecho": match.group(0),
            "dica": "Adicione um espaço após a pontuação.",
        })

    # 5. Informalidades (pra, né, tipo assim, etc.)
    ja_alerta = set()
    for padrao, (palavra, dica) in INFORMALIDADES.items():
        matches = list(re.finditer(padrao, texto_lower))
        if matches and palavra not in ja_alerta:
            ja_alerta.add(palavra)
            erros.append({
                "tipo": "informalidade",
                "regra": f"Linguagem informal: '{palavra}'",
                "trecho": matches[0].group(0),
                "dica": dica,
            })

    # 6. Primeira pessoa (evitar em textos acadêmicos)
    trechos_p1 = []
    for padrao in PRIMEIRA_PESSOA_PADROES:
        for match in re.finditer(padrao, texto_lower):
            t = match.group(0)
            if t not in trechos_p1:
                trechos_p1.append(t)
            if len(trechos_p1) >= 5:
                break
        if len(trechos_p1) >= 5:
            break

    if trechos_p1:
        erros.append({
            "tipo": "pessoa",
            "regra": "Uso de primeira pessoa",
            "trecho": ", ".join(trechos_p1),
            "dica": "Textos acadêmicos devem ser escritos em 3ª pessoa (impessoal). Evite 'eu', 'nós', 'meu', 'acho', 'penso'.",
        })

    return erros