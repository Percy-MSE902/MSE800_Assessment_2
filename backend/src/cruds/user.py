from sqlalchemy.orm import Session
from cruds.CRUDBase import CRUDBase
from models.user import UserModel
from schemas.user import UserCreateSchema,UserUpdateSchema

# CRUD Functions
class user(CRUDBase[UserModel, UserCreateSchema, UserUpdateSchema]):
    pass