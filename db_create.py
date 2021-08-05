import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class Apartmets(Base):
    __tablename__ = 'apartments'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    price = Column(String(250), nullable=False)
    link = Column(String(250), nullable=False)


engine = create_engine('sqlite:///apartmentsDB.db')
Base.metadata.create_all(engine)
