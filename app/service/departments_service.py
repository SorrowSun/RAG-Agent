from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dto.dto import Department


def get_departments_service(db: Session):
    departments = db.scalars(select(Department)).all()
    return [
        {
            "id": department.id,
            "name": department.name,
            "status": department.status,
        }
        for department in departments
    ]
