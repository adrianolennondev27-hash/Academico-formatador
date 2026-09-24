from pydantic import BaseModel


class MetadadosABNT(BaseModel):
    instituicao: str
    curso: str
    titulo: str
    aluno: str
    professor: str = ""
    cidade: str
    ano: str
    texto_limpo: str
    incluir_folha_rosto: bool = False
    natureza_trabalho: str = ""
    incluir_sumario: bool = False