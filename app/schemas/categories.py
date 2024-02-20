from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Category(BaseModel):
    id: Optional[int]
    name: str
    level: int
    created_at: datetime
    updated_at: datetime
    children_ids: List[str]
    parent_id: Optional[int]

    class Config:
        orm_mode = True
