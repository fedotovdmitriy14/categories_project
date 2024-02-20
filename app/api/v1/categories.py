from typing import Dict, Optional

from fastapi import APIRouter, Depends, Body

from app.services.categories import get_base_service, BaseService

router = APIRouter()


@router.post(
    '/',
)
async def post_new_category(
    parent_id: Optional[int] = Body(None),
    name: str = Body(...),
    base_service: BaseService = Depends(get_base_service)
) -> Dict[str, str]:
    await base_service.save(name=name, parent_id=parent_id)
    return {'message': 'ok'}


@router.get(
    '/',
)
async def get_categories():
    pass
