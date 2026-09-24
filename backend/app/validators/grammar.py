import re

def verificar_gramatica(texto: str):
    erros = []
    
    # 1. "a" no lugar de "há" (tempo decorrido) - aceita quantificadores no meio
    padrao_a_ha = re.compile(
        r'\ba\s+(?:\w+\s+)*(?:dias?|meses?|anos?|horas?|minutos?|semanas?|décadas?)\b',
        re.IGNORECASE
    )
    for match in padrao_a_ha.finditer(texto):
        erros.append({
            "tipo": "gramatica",
            "regra": "Uso de 'a' no lugar de 'há'",
            "trecho": match.group(0),
            "dica": "Você quis dizer 'há'? (Ex: 'há dois anos' indica tempo passado)"
        })

    # 2. "mais" no lugar de "mas"
    padrao_mais_mas = re.compile(
        r'\bmais\b(?=\s+(não|sim|é|foi|está|era|será|o|a|os|as)\b)',
        re.IGNORECASE
    )
    for match in padrao_mais_mas.finditer(texto):
        erros.append({
            "tipo": "gramatica",
            "regra": "Possível uso incorreto de 'mais' (em vez de 'mas')",
            "trecho": match.group(0),
            "dica": "Verifique se o correto seria 'mas' (conjunção adversativa)."
        })

    # 3. Espaço antes de pontuação
    padrao_espaco_pontuacao = re.compile(r'\s+([,.;:!?])')
    for match in padrao_espaco_pontuacao.finditer(texto):
        erros.append({
            "tipo": "pontuacao",
            "regra": "Espaço antes de pontuação",
            "trecho": match.group(0),
            "dica": "Remova o espaço antes da pontuação."
        })

    # 4. Falta de espaço depois de pontuação
    padrao_falta_espaco = re.compile(r'([,.;:!?])(?=[A-Za-zÀ-ÿ])')
    for match in padrao_falta_espaco.finditer(texto):
        erros.append({
            "tipo": "pontuacao",
            "regra": "Falta de espaço após pontuação",
            "trecho": match.group(0),
            "dica": "Adicione um espaço após a pontuação."
        })

    return erros