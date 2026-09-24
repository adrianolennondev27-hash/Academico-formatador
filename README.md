# FVA - Formatador e Validador Academico

Ferramenta web gratuita, independente e privada para estudantes universitarios.

## Regra de ouro

Nunca reescreve o texto do aluno - apenas alerta onde ele fugiu do padrao.

## Funcionalidades

- Conversao de formatos (PDF, Word, ODT)
- Formatacao ABNT completa (capa, folha de rosto, sumario, referencias)
- Numeracao de paginas automatica
- Validacao ortografica, gramatical e estrutural
- Multiplos autores separados por virgula

## Como rodar

Backend:
  cd backend
  .\venv\Scripts\activate
  python -m uvicorn app.main:app --reload

Frontend:
  cd frontend
  npm install
  npm run dev

Acesse: http://localhost:3000

