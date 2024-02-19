from typing import Dict, Optional

from fastapi import APIRouter, Depends, Body

from app.db.engine import get_db, SessionLocal
from app.services.categories import save_to_db

router = APIRouter()


@router.post(
    '/',
)
async def post_new_category(
    parent_id: Optional[int] = Body(None),
    name: str = Body(...),
    db: SessionLocal = Depends(get_db)
) -> Dict[str, str]:
    save_to_db(db, name=name, parent_id=parent_id)
    return {'message': 'ok'}
