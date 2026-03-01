import math
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional

from database import get_db
from models.user import UserModel
from core.dependencies import get_current_user, require_permission
from schemas.housekeeping import InventoryItemSchema, InventoryItemCreateSchema
from services.inventory import InventoryService
from schemas.PaginationRequest import PaginationRequest


router = APIRouter(prefix='/api/inventory', tags=['inventory'])


@router.get('/', response_model=List[InventoryItemSchema])
def read_all(
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = InventoryService(db)
    return service.get_all()


@router.get('/{item_id}', response_model=InventoryItemSchema)
def read_item(
    item_id: int,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = InventoryService(db)
    item = service.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')
    return item


@router.post('/', response_model=InventoryItemSchema)
def create_item(
    item_in: InventoryItemCreateSchema,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = InventoryService(db)
    return service.create(item_in)


@router.put('/{item_id}', response_model=InventoryItemSchema)
def update_item(
    item_id: int,
    item_in: dict,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = InventoryService(db)
    item = service.update(item_id, item_in)
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')
    return item


@router.delete('/{item_id}')
def delete_item(
    item_id: int,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = InventoryService(db)
    result = service.delete(item_id)
    if not result:
        raise HTTPException(status_code=404, detail='Item not found')
    return {'ok': True}


@router.post('/restock/{item_id}')
def restock(
    item_id: int,
    quantity: int,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = InventoryService(db)
    item = service.restock(item_id, quantity)
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')
    return item


@router.get('/low-stock/list', response_model=List[InventoryItemSchema])
def get_low_stock(
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = InventoryService(db)
    return service.get_low_stock()


@router.post('/paginated')
def read_paginated(
    pageParam: PaginationRequest,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    filter_dict: Dict[str, Any] = {}
    if pageParam.filters:
        filter_dict = pageParam.filters

    service = InventoryService(db)
    total, items = service.get_paginated(
        page=pageParam.page,
        page_size=pageParam.page_size,
        filters=filter_dict
    )
    return {
        "current_page": pageParam.page,
        "page_total": math.ceil(total / pageParam.page_size) if pageParam.page_size > 0 else 0,
        "total": total,
        "items": [InventoryItemSchema.model_validate(item, from_attributes=True) for item in items]
    }
