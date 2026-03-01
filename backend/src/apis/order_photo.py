from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database import get_db
from models.user import UserModel
from models.service_order import OrderPhotoModel
from core.dependencies import get_current_user, require_permission
from schemas.housekeeping import OrderPhotoSchema, OrderPhotoCreateSchema
from cruds.order_photo import OrderPhotoService


router = APIRouter(prefix='/api/order-photo', tags=['order-photo'])


class ReorderSchema(BaseModel):
    photo_ids: List[int]


@router.get('/order/{order_id}', response_model=List[OrderPhotoSchema])
def get_photos_by_order(
    order_id: int,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = OrderPhotoService(db)
    return service.get_by_order(order_id)


@router.post('/', response_model=OrderPhotoSchema)
def create_photo(
    photo_in: OrderPhotoCreateSchema,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = OrderPhotoService(db)
    return service.create(photo_in, current_user.id)


@router.post('/reorder')
def reorder_photos(
    reorder_data: ReorderSchema,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    for index, photo_id in enumerate(reorder_data.photo_ids):
        photo = db.query(OrderPhotoModel).filter(OrderPhotoModel.id == photo_id).first()
        if photo:
            photo.sort_order = index
    db.commit()
    return {'ok': True}


@router.delete('/{photo_id}')
def delete_photo(
    photo_id: int,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = OrderPhotoService(db)
    result = service.delete(photo_id)
    if not result:
        raise HTTPException(status_code=404, detail='Photo not found')
    return {'ok': True}
