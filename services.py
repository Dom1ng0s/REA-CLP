# services.py
from sqlalchemy.orm import Session
from database import AlunoDB, READB, TagDB

class Repositorio:
    def __init__(self, db: Session):
        self.db = db

    def obter_aluno(self, aluno_id: str):
        return self.db.query(AlunoDB).filter(AlunoDB.id == aluno_id).first()

    def cadastrar_interesses(self, aluno_id: str, tags: list[str]):
        aluno = self.obter_aluno(aluno_id)
        if not aluno:
            return None
        
        aluno.interesses = [] # Limpa interesses antigos
        for nome_tag in tags:
            tag = self.db.query(TagDB).filter(TagDB.nome == nome_tag).first()
            if not tag:
                tag = TagDB(nome=nome_tag)
                self.db.add(tag)
            aluno.interesses.append(tag)
        self.db.commit()
        return aluno
    def cadastrar_rea(self, titulo: str, tags: list[str]):
        """Implementa o Diagrama de Atividades: Catalogar REA"""
        novo_rea = READB(titulo=titulo)
        
        for nome_tag in tags:
            # Verifica se a tag já existe no banco
            tag = self.db.query(TagDB).filter(TagDB.nome == nome_tag).first()
            if not tag:
                # Se não existir, cria uma nova tag
                tag = TagDB(nome=nome_tag)
                self.db.add(tag)
            
            # Vincula a tag ao REA
            novo_rea.tags.append(tag)
            
        self.db.add(novo_rea)
        self.db.commit()
        return novo_rea

    def listar_reas(self):
        """Busca todos os recursos catalogados"""
        return self.db.query(READB).all()

class MotorRecomendacao:
    def __init__(self, db: Session):
        self.db = db

    def gerar_recomendacoes(self, aluno: AlunoDB):
        """
        Implementa a lógica baseada em conteúdo:
        Busca REAs que possuam as mesmas tags de interesse do aluno.
        """
        nomes_interesses = [tag.nome for tag in aluno.interesses]
        
        # Se não tem interesses, o diagrama diz para solicitar o preenchimento
        if not nomes_interesses:
            return {"status": "perfil_incompleto", "reas": []}

        # Busca REAs que tenham pelo menos uma tag em comum com o aluno
        reas_recomendados = self.db.query(READB).filter(
            READB.tags.any(TagDB.nome.in_(nomes_interesses))
        ).all()

        # Aqui entraria o cálculo de "Score" no futuro (ex: IA, histórico de avaliações)
        return {
            "status": "sucesso", 
            "reas": [{"id": rea.id, "titulo": rea.titulo} for rea in reas_recomendados]
        }