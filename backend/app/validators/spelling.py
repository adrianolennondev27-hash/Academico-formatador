from spellchecker import SpellChecker

# Carrega o dicionário de Português
spell = SpellChecker(language='pt')

def verificar_ortografia(texto: str):
    # Divide o texto em palavras e remove pontuações básicas
    palavras = texto.split()
    palavras_limpas = [p.strip('.,;:!?()[]{}"\'') for p in palavras]
    palavras_limpas = [p for p in palavras_limpas if p and p.isalpha()]
    
    # Encontra palavras desconhecidas
    palavras_erradas = spell.unknown(palavras_limpas)
    
    erros = []
    for palavra in palavras_erradas:
        sugestoes = spell.candidates(palavra)
        erros.append({
            "palavra": palavra,
            "sugestoes": list(sugestoes)[:3] if sugestoes else []
        })
    return erros