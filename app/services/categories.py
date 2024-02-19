from datetime import datetime
from typing import Optional

from app.db.engine import SessionLocal
from app.db.models.categories import Categories


def save_to_db(db: SessionLocal, name: str, parent_id: Optional[int]):
    if not parent_id:
        data_to_insert = Categories(
            name=name,
            is_final=True,
            parent_ids=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(data_to_insert)
        db.commit()
    else:
        selected_category = db.query(Categories).filter(Categories.id == parent_id).first()
        if selected_category:
            selected_category.is_final = False
            if parent_ids := selected_category.parent_ids:
                new_parent_ids = [parent_id for parent_id in parent_ids]
                new_parent_ids.append(selected_category.id)
            else:
                new_parent_ids = [selected_category.id]
            data_to_insert = Categories(
                name=name,
                is_final=True,
                parent_ids=new_parent_ids,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.add(selected_category)
            db.add(data_to_insert)
            db.commit()
