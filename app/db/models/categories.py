from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    level = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    children_ids = Column(JSON)
    parent_id = Column(Integer)
