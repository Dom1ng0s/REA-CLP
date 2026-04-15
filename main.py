# main.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, AlunoDB, READB, TagDB
from services import Repositorio, MotorRecomendacao

app = FastAPI(title="Motor de Recomendação REA")

# Dependência para injetar o banco de dados nas rotas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- SCHEMAS (Pydantic para validar entrada de dados) ---
class InteressesRequest(BaseModel):
    tags: list[str]

# --- ENDPOINTS ---

@app.get("/recomendacoes/{aluno_id}")
def obter_recomendacoes(aluno_id: str, db: Session = Depends(get_db)):
    """Fluxo Principal do Diagrama de Sequência"""
    repo = Repositorio(db)
    aluno = repo.obter_aluno(aluno_id)
    
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")

    motor = MotorRecomendacao(db)
    resultado = motor.gerar_recomendacoes(aluno)
    
    return resultado

@app.post("/alunos/{aluno_id}/interesses")
def atualizar_interesses(aluno_id: str, request: InteressesRequest, db: Session = Depends(get_db)):
    """Fluxo alternativo: Cadastrar Perfil (Diagrama de Atividades)"""
    repo = Repositorio(db)
    aluno = repo.cadastrar_interesses(aluno_id, request.tags)
    
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")
    
    return {"mensagem": "Interesses atualizados com sucesso", "interesses": request.tags}

# --- ROTA AUXILIAR PARA POPULAR O BANCO DE TESTE ---
@app.post("/setup-teste")
def criar_dados_iniciais(db: Session = Depends(get_db)):
    """Use esta rota apenas uma vez para criar dados falsos no banco e testar"""
    # Cria um aluno
    aluno = AlunoDB(nome="Davi", email="davi@teste.com")
    
    # Cria alguns REAs
    rea1 = READB(titulo="Curso de Python Avançado")
    rea1.tags.append(TagDB(nome="programação"))
    rea1.tags.append(TagDB(nome="python"))

    rea2 = READB(titulo="Introdução ao Cálculo")
    rea2.tags.append(TagDB(nome="matemática"))

    db.add_all([aluno, rea1, rea2])
    db.commit()
    
    return {"mensagem": "Dados iniciais criados!", "aluno_id": aluno.id}
