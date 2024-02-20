from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, JSON, inspect
from sqlalchemy.orm import declarative_base, as_declarative

Base = declarative_base()


@as_declarative()
class Base:
    def _asdict(self):
        return {c.key: str(getattr(self, c.key)) if isinstance(getattr(self, c.key), datetime) else getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    level = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    children_ids = Column(JSON)
    parent_id = Column(Integer)
