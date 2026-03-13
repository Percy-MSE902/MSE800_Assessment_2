from sqlalchemy.orm import Session

from cruds.CRUDBase import CRUDBase
from model.service_order import OrderPhotoModel
from schemas.housekeeping import OrderPhotoSchema, OrderPhotoCreateSchema



class OrderPhotoService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = CRUDBase(OrderPhotoModel)

    def get_all(self):
        return self.crud.get_all(self.db)

    def get(self, id: int):
        return self.crud.get(self.db, id)

    def get_by_order(self, order_id: int):
        return self.db.query(OrderPhotoModel).filter(
            OrderPhotoModel.order_id == order_id,
            OrderPhotoModel.is_deleted == 0
        ).order_by(OrderPhotoModel.sort_order.asc()).all()

    def create(self, obj_in: OrderPhotoCreateSchema, uploaded_by: int):
        data = obj_in.dict()
        data['uploaded_by'] = uploaded_by

        max_order = self.db.query(OrderPhotoModel).filter(
            OrderPhotoModel.order_id == obj_in.order_id,
            OrderPhotoModel.photo_type == obj_in.photo_type,
            OrderPhotoModel.is_deleted == 0
        ).count()
        data['sort_order'] = max_order

        obj = OrderPhotoModel(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def reorder_photos(self, photo_ids: list):
        for index, photo_id in enumerate(photo_ids):
            photo = self.db.query(OrderPhotoModel).filter(OrderPhotoModel.id == photo_id).first()
            if photo:
                photo.sort_order = index
        self.db.commit()
        return {'ok': True}

    def delete(self, id: int):
        db_obj = self.crud.get(self.db, id)
        if not db_obj:
            return False
        return self.crud.soft_delete(self.db, db_obj)
