from datetime import datetime
from typing import Optional

from sqlalchemy.orm.attributes import flag_modified

from app.db.engine import SessionLocal
from app.db.models.categories import Categories


def save_to_db(db: SessionLocal, name: str, parent_id: Optional[int]):
    if not parent_id:
        data_to_insert = Categories(
            name=name,
            level=1,
            children_ids=[],
            parent_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(data_to_insert)
        db.commit()
    else:
        selected_category = db.query(Categories).filter(Categories.id == parent_id).first()
        if selected_category:
            data_to_insert = Categories(
                name=name,
                children_ids=[],
                level=selected_category.level + 1,
                parent_id=selected_category.id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.add(data_to_insert)
            db.flush()
            selected_category.children_ids.append(data_to_insert.id)
            flag_modified(selected_category, 'children_ids')
            db.add(selected_category)
            db.commit()
