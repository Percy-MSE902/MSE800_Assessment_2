from sqlalchemy.orm import Session
from cruds.CRUDBase import CRUDBase
from models.room import RoomModel
from schemas.housekeeping import RoomCreateSchema, RoomUpdateSchema


class RoomCRUD(CRUDBase[RoomModel, RoomCreateSchema, RoomUpdateSchema]):
    pass


room_crud = RoomCRUD(RoomModel)


class RoomService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return room_crud.get_all(self.db)

    def get(self, id: int):
        return room_crud.get(self.db, id)

    def create(self, obj_in: RoomCreateSchema):
        return room_crud.create(self.db, obj_in)

    def update(self, id: int, obj_in: RoomUpdateSchema):
        db_obj = room_crud.get(self.db, id)
        if not db_obj:
            return None
        return room_crud.update(self.db, db_obj, obj_in)

    def delete(self, id: int):
        db_obj = room_crud.get(self.db, id)
        if not db_obj:
            return False
        return room_crud.soft_delete(self.db, db_obj)

    def get_paginated(self, page: int = 1, page_size: int = 10, filters: dict = None, order_by: str = None):
        skip = (page - 1) * page_size
        return room_crud.get_paginated(self.db, skip, page_size, filters, order_by)

    def update_status(self, room_id: int, status: int):
        room = room_crud.get(self.db, room_id)
        if not room:
            return None
        room.status = status
        self.db.commit()
        self.db.refresh(room)
        return room

    def get_available_rooms(self):
        return room_crud._base_query(self.db).filter(RoomModel.status == 0).all()
