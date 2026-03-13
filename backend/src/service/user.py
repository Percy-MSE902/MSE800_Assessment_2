from sqlalchemy.orm import Session

from cruds.CRUDBase import CRUDBase
from model.user import UserModel
from schemas.housekeeping import UserCreateSchema, UserUpdateSchema



class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = CRUDBase(UserModel)

    def get_all(self):
        return self.crud.get_all(self.db)

    def get(self, id: int):
        return self.crud.get(self.db, id)

    def create(self, item_in: UserCreateSchema):
        user = UserModel(**item_in.dict())
        user.set_password(item_in.password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, id: int, item_in: UserUpdateSchema):
        db_obj = self.crud.get(self.db, id)
        if not db_obj:
            return None
        return self.crud.update(self.db, db_obj, item_in)

    def delete(self, id: int):
        db_obj = self.crud.get(self.db, id)
        if not db_obj:
            return None
        self.crud.soft_delete(self.db, db_obj)
        return {'ok': True}

    def get_by_role(self, role: str):
        return self.crud._base_query(self.db).filter(UserModel.role == role).all()
