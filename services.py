# services.py
from sqlalchemy.orm import Session
from database import AlunoDB, READB, TagDB
from typing import Optional

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

    def buscar_reas_por_tag(self, tag_nome: str):
        """Busca materiais educacionais que contenham uma tag específica"""
        # O SQLAlchemy usa o '.any()' para procurar dentro de listas de relacionamentos (N:N)
        return self.db.query(READB).filter(
            READB.tags.any(TagDB.nome == tag_nome)
        ).all()
    def deletar_rea(self, rea_id: str) -> bool:
        """Deleta um material do banco de dados (O 'D' do CRUD)"""
        rea = self.db.query(READB).filter(READB.id == rea_id).first()
        
        if rea:
            self.db.delete(rea)
            self.db.commit()
            return True
            
        return False
    def atualizar_rea(self, rea_id: str, titulo: Optional[str] = None, tags: Optional[list[str]] = None):
        """O 'U' do CRUD: Agora dentro da classe e com suporte a update parcial"""
        rea = self.db.query(READB).filter(READB.id == rea_id).first()
        
        if not rea:
            return None
            
        if titulo is not None:
            rea.titulo = titulo
        
        if tags is not None:
            novas_tags_db = []
            for nome_tag in tags:
                nome_limpo = nome_tag.lower().strip()
                tag_existente = self.db.query(TagDB).filter(TagDB.nome == nome_limpo).first()
                
                if not tag_existente:
                    tag_existente = TagDB(nome=nome_limpo)
                    self.db.add(tag_existente)
                    self.db.flush()
                
                novas_tags_db.append(tag_existente)
            
            rea.tags = novas_tags_db
        
        try:
            self.db.commit()
            self.db.refresh(rea)
            return rea
        except Exception as e:
            self.db.rollback()
            raise e

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