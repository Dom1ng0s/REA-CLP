# database.py
from sqlalchemy import create_engine, Column, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from uuid import uuid4

SQLALCHEMY_DATABASE_URL = "sqlite:///./banco.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def gerar_uuid():
    return str(uuid4())

# 1. Tabelas associativas 
aluno_interesse_table = Table(
    'aluno_interesse', Base.metadata,
    Column('aluno_id', String, ForeignKey('alunos.id')),
    Column('tag_nome', String, ForeignKey('tags.nome')) 
)

rea_tag_table = Table(
    'rea_tag', Base.metadata,
    Column('rea_id', String, ForeignKey('reas.id')),
    Column('tag_nome', String, ForeignKey('tags.nome'))
)

# 2. Modelos limpos, usando apenas a string 'secondary' com o nome da variável
class TagDB(Base):
    __tablename__ = "tags"
    nome = Column(String, primary_key=True)

class AlunoDB(Base):
    __tablename__ = "alunos"
    id = Column(String, primary_key=True, default=gerar_uuid)
    email = Column(String, unique=True, index=True)
    nome = Column(String)
    
    # Aqui está o pulo do gato: referenciando diretamente a variável da tabela
    interesses = relationship("TagDB", secondary=aluno_interesse_table)

class READB(Base):
    __tablename__ = "reas"
    id = Column(String, primary_key=True, default=gerar_uuid)
    titulo = Column(String)
    
    # Mesma coisa aqui
    tags = relationship("TagDB", secondary=rea_tag_table)

Base.metadata.create_all(bind=engine)