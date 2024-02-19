from sqlalchemy import Boolean, Column, String, Integer, DateTime, JSON
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    parent_ids = Column(JSON)
    is_final = Column(Boolean)
