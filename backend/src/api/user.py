from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, require_permission, get_service
from service.user import UserService
from model.user import UserModel
from schemas.housekeeping import UserSchema, UserCreateSchema, UserUpdateSchema




router = APIRouter(prefix='/api/user', tags=['user'])
public_router = APIRouter(prefix='/api/user', tags=['user'])


@router.get('/', response_model=List[UserSchema])
def read_all(
    current_user: UserModel = Depends(require_permission()),
    service: UserService = Depends(get_service(UserService))
):
    return service.get_all()


@router.get('/{id}', response_model=UserSchema)
def read_item(
    id: int,
    current_user: UserModel = Depends(require_permission()),
    service: UserService = Depends(get_service(UserService))
):
    db_obj = service.get(id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return db_obj


@public_router.post('/', response_model=UserSchema)
def create_item(
    item_in: UserCreateSchema,
    service: UserService = Depends(get_service(UserService))
):
    return service.create(item_in)


@router.put('/{id}', response_model=UserSchema)
def update_item(
    id: int,
    item_in: UserUpdateSchema,
    current_user: UserModel = Depends(require_permission()),
    service: UserService = Depends(get_service(UserService))
):
    db_obj = service.update(id, item_in)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return db_obj


@router.delete('/{id}')
def delete_item(
    id: int,
    current_user: UserModel = Depends(require_permission()),
    service: UserService = Depends(get_service(UserService))
):
    result = service.delete(id)
    if not result:
        raise HTTPException(status_code=404, detail='Item not found')
    return result


@router.get('/role/{role}', response_model=List[UserSchema])
def get_users_by_role(
    role: str,
    current_user: UserModel = Depends(require_permission()),
    service: UserService = Depends(get_service(UserService))
):
    return service.get_by_role(role)
