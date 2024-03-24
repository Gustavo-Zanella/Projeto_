from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Empresa(Base):
    __tablename__ = 'tbempresa'

    empcnpj = Column(String, primary_key=True)
    empnumerofuncionarios = Column(String)
    empfatanualestimado = Column(String)
    empvendedor = Column(String)
