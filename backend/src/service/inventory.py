from typing import List, Optional

from sqlalchemy.orm import Session

from cruds.CRUDBase import CRUDBase
from model.inventory_item import InventoryItemModel
from schemas.housekeeping import InventoryItemCreateSchema



class InventoryCRUD(CRUDBase[InventoryItemModel, InventoryItemCreateSchema, dict]):
    pass


inventory_crud = InventoryCRUD(InventoryItemModel)


class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return inventory_crud.get_all(self.db)

    def get(self, id: int):
        return inventory_crud.get(self.db, id)

    def create(self, obj_in: InventoryItemCreateSchema):
        return inventory_crud.create(self.db, obj_in)

    def update(self, id: int, data: dict):
        db_obj = inventory_crud.get(self.db, id)
        if not db_obj:
            return None
        for key, value in data.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int):
        db_obj = inventory_crud.get(self.db, id)
        if not db_obj:
            return False
        return inventory_crud.soft_delete(self.db, db_obj)

    def get_paginated(self, page: int = 1, page_size: int = 10, filters: dict = None):
        skip = (page - 1) * page_size
        return inventory_crud.get_paginated(self.db, skip, page_size, filters)

    def restock(self, item_id: int, quantity: int):
        item = inventory_crud.get(self.db, item_id)
        if not item:
            return None
        item.quantity += quantity
        self.db.commit()
        self.db.refresh(item)
        return item

    def consume(self, item_id: int, quantity: int):
        item = inventory_crud.get(self.db, item_id)
        if not item:
            return None
        if item.quantity < quantity:
            raise ValueError("Insufficient inventory")
        item.quantity -= quantity
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_low_stock(self):
        items = inventory_crud.get_all(self.db)
        return [item for item in items if item.quantity <= item.min_stock]
