from sqlalchemy import JSON, Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    level = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    children_ids = Column(JSON)
    parent_id = Column(Integer)
