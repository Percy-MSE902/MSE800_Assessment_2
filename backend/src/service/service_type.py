from typing import Optional

from sqlalchemy.orm import Session
from pydantic import BaseModel

from model.service_type import ServiceTypeModel



class ServiceTypeService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(ServiceTypeModel).filter(ServiceTypeModel.is_deleted == 0).all()

    def get(self, type_id: int):
        return self.db.query(ServiceTypeModel).filter(ServiceTypeModel.type_id == type_id).first()

    def create(self, type_name: str, description: str = None, standard_time: int = 30, price: float = 0):
        item = ServiceTypeModel(
            type_name=type_name,
            description=description,
            standard_time=standard_time,
            price=price,
            is_active=1
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, type_id: int, item_in: dict):
        item = self.db.query(ServiceTypeModel).filter(ServiceTypeModel.type_id == type_id).first()
        if not item:
            return None
        for key, value in item_in.items():
            if hasattr(item, key):
                setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, type_id: int):
        item = self.db.query(ServiceTypeModel).filter(ServiceTypeModel.type_id == type_id).first()
        if not item:
            return None
        item.is_deleted = 1
        self.db.commit()
        return item
