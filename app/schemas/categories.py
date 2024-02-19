from pydantic import BaseModel


class CategoryInsertField(BaseModel):
    name: str
