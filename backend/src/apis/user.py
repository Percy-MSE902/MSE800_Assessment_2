from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import UserModel
from core.dependencies import get_current_user, require_permission
from schemas.housekeeping import UserSchema, UserCreateSchema, UserUpdateSchema
from cruds.CRUDBase import CRUDBase


router = APIRouter(prefix='/api/user', tags=['user'])
public_router = APIRouter(prefix='/api/user', tags=['user'])

user_crud = CRUDBase(UserModel)


@router.get('/', response_model=List[UserSchema])
def read_all(db: Session = Depends(get_db), current_user: UserModel = Depends(require_permission())):
    return user_crud.get_all(db)


@router.get('/{id}', response_model=UserSchema)
def read_item(id, db: Session = Depends(get_db), current_user: UserModel = Depends(require_permission())):
    db_obj = user_crud.get(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return db_obj


@public_router.post('/', response_model=UserSchema)
def create_item(item_in: UserCreateSchema, db: Session = Depends(get_db)):
    user = UserModel(**item_in.dict())
    user.set_password(item_in.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put('/{id}', response_model=UserSchema)
def update_item(id, item_in: UserUpdateSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(require_permission())):
    db_obj = user_crud.get(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return user_crud.update(db, db_obj, item_in)


@router.delete('/{id}')
def delete_item(id, db: Session = Depends(get_db), current_user: UserModel = Depends(require_permission())):
    db_obj = user_crud.get(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    user_crud.soft_delete(db, db_obj)
    return {'ok': True}


@router.get('/role/{role}', response_model=List[UserSchema])
def get_users_by_role(role: str, db: Session = Depends(get_db), current_user: UserModel = Depends(require_permission())):
    return user_crud._base_query(db).filter(UserModel.role == role).all()
