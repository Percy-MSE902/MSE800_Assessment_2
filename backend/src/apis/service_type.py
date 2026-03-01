from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
from models.user import UserModel
from models.service_type import ServiceTypeModel
from core.dependencies import get_current_user, require_permission


router = APIRouter(prefix='/api/service-type', tags=['service-type'])


class ServiceTypeSchema(BaseModel):
    type_id: Optional[int] = None
    type_name: str
    description: Optional[str] = None
    standard_time: int = 30
    price: float
    is_active: int = 1

    class Config:
        from_attributes = True


class ServiceTypeCreateSchema(BaseModel):
    type_name: str
    description: Optional[str] = None
    standard_time: int = 30
    price: float


@router.get('/', response_model=List[ServiceTypeSchema])
def get_all(
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    return db.query(ServiceTypeModel).filter(ServiceTypeModel.is_deleted == 0).all()


@router.get('/{type_id}', response_model=ServiceTypeSchema)
def get_item(
    type_id: int,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    item = db.query(ServiceTypeModel).filter(ServiceTypeModel.type_id == type_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Service type not found')
    return item


@router.post('/', response_model=ServiceTypeSchema)
def create_item(
    item_in: ServiceTypeCreateSchema,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    item = ServiceTypeModel(**item_in.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put('/{type_id}', response_model=ServiceTypeSchema)
def update_item(
    type_id: int,
    item_in: dict,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    item = db.query(ServiceTypeModel).filter(ServiceTypeModel.type_id == type_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Service type not found')
    for key, value in item_in.items():
        if hasattr(item, key):
            setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete('/{type_id}')
def delete_item(
    type_id: int,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    item = db.query(ServiceTypeModel).filter(ServiceTypeModel.type_id == type_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Service type not found')
    item.is_deleted = 1
    db.commit()
    return {'ok': True}
