import re


def validar_resenha_critica(texto: str):
    alertas = []
    texto_lower = texto.lower()

    verbos_resumo = len(
        re.findall(
            r"\b(o autor|a obra|o livro|o texto|descreve|apresenta|resume|relata|aborda)\b",
            texto_lower,
        )
    )

    verbos_critica = len(
        re.findall(
            r"\b(acredito|penso|critico|avali(o|ação)|no entanto|por outro lado|entretanto|falha|positivo|negativo|concluo|considero|é importante)\b",
            texto_lower,
        )
    )

    if verbos_resumo > verbos_critica * 1.5:
        alertas.append({
            "tipo": "estrutura",
            "regra": "Falta de análise crítica",
            "dica": "Seu texto parece ser apenas um resumo descritivo da obra. Uma resenha crítica exige posicionamento, avaliação e análise.",
        })

    if verbos_critica == 0:
        alertas.append({
            "tipo": "estrutura",
            "regra": "Ausência de posicionamento",
            "dica": "Não encontramos marcas de opinião ou análise. Uma resenha crítica precisa que você se posicione sobre a obra.",
        })

    return alertas


def validar_artigo_tcc(texto: str):
    alertas = []
    texto_lower = texto.lower()

    secoes = {
        "introdução": r"\b(introdução|introducao)\b",
        "desenvolvimento": r"\b(desenvolvimento|metodologia|materiais e métodos|referencial teórico)\b",
        "conclusão": r"\b(conclusão|conclusao|considerações finais)\b",
    }

    for nome_secao, padrao in secoes.items():
        if not re.search(padrao, texto_lower):
            alertas.append({
                "tipo": "estrutura",
                "regra": f"Seção '{nome_secao.capitalize()}' ausente",
                "dica": f"Um trabalho acadêmico completo deve conter a seção de {nome_secao}.",
            })

    return alertas


def validar_resumo(texto: str):
    alertas = []
    palavras = len(texto.split())

    if palavras > 500:
        alertas.append({
            "tipo": "estrutura",
            "regra": "Resumo muito longo",
            "dica": f"Seu resumo tem {palavras} palavras. O ideal é que um resumo acadêmico tenha entre 150 e 500 palavras.",
        })

    if palavras < 100:
        alertas.append({
            "tipo": "estrutura",
            "regra": "Resumo muito curto",
            "dica": f"Seu resumo tem {palavras} palavras. O ideal é que um resumo acadêmico tenha entre 150 e 500 palavras.",
        })

    if re.search(r"\b(eu|acredito|penso|na minha opinião)\b", texto.lower()):
        alertas.append({
            "tipo": "estrutura",
            "regra": "Uso de primeira pessoa no resumo",
            "dica": "Resumos acadêmicos devem ser escritos em terceira pessoa, sem opiniões pessoais.",
        })

    return alertas


def validar_trabalho_academico(texto: str):
    alertas = []
    palavras = len(texto.split())
    texto_lower = texto.lower()

    if palavras < 100:
        alertas.append({
            "tipo": "estrutura",
            "regra": "Texto muito curto",
            "dica": f"Seu trabalho tem apenas {palavras} palavras. Trabalhos acadêmicos geralmente exigem um desenvolvimento mínimo.",
        })

    # Linguagem informal (mesmos padrões do grammar.py para consistência)
    padrao_informal = r"\b(tipo assim|né|pra|pro|tá|vc|pq|qdo|mt|blz|galera|bagunça|cara|daí|meio que)\b"
    if re.search(padrao_informal, texto_lower):
        alertas.append({
            "tipo": "estrutura",
            "regra": "Linguagem informal detectada",
            "dica": "Evite gírias e abreviações em trabalhos acadêmicos. Prefira a norma culta da língua portuguesa.",
        })

    # Primeira pessoa
    if re.search(r"\b(eu|nós|meu|minha|acho|penso|acredito|considero)\b", texto_lower):
        alertas.append({
            "tipo": "estrutura",
            "regra": "Uso de primeira pessoa",
            "dica": "Trabalhos acadêmicos devem ser escritos em 3ª pessoa (impessoal). Evite 'eu', 'nós', 'acho', 'penso'.",
        })

    return alertas


def validar_estrutura(texto: str, tipo_trabalho: str):
    if tipo_trabalho == "resenha":
        return validar_resenha_critica(texto)
    elif tipo_trabalho in ["tcc", "artigo"]:
        return validar_artigo_tcc(texto)
    elif tipo_trabalho == "resumo":
        return validar_resumo(texto)
    elif tipo_trabalho in ["trabalho", "trabalho_academico"]:
        return validar_trabalho_academico(texto)
    else:
        return [{
            "tipo": "erro",
            "regra": "Tipo desconhecido",
            "dica": "Escolha um tipo de trabalho válido.",
        }]