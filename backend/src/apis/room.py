import math
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional

from database import get_db
from models.user import UserModel
from core.dependencies import get_current_user, require_permission
from schemas.housekeeping import RoomSchema, RoomCreateSchema, RoomUpdateSchema
from services.room import RoomService
from schemas.PaginationRequest import PaginationRequest


router = APIRouter(prefix='/api/room', tags=['room'])


@router.get('/', response_model=List[RoomSchema])
def read_all(
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = RoomService(db)
    return service.get_all()


@router.get('/{room_id}', response_model=RoomSchema)
def read_item(
    room_id: int,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = RoomService(db)
    room = service.get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail='Room not found')
    return room


@router.post('/', response_model=RoomSchema)
def create_item(
    item_in: RoomCreateSchema,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = RoomService(db)
    return service.create(item_in)


@router.put('/{room_id}', response_model=RoomSchema)
def update_item(
    room_id: int,
    item_in: RoomUpdateSchema,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = RoomService(db)
    room = service.update(room_id, item_in)
    if not room:
        raise HTTPException(status_code=404, detail='Room not found')
    return room


@router.delete('/{room_id}')
def delete_item(
    room_id: int,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = RoomService(db)
    result = service.delete(room_id)
    if not result:
        raise HTTPException(status_code=404, detail='Room not found')
    return {'ok': True}


@router.get('/available/list', response_model=List[RoomSchema])
def get_available(
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = RoomService(db)
    return service.get_available_rooms()


@router.put('/{room_id}/status')
def update_status(
    room_id: int,
    status: int,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    service = RoomService(db)
    room = service.update_status(room_id, status)
    if not room:
        raise HTTPException(status_code=404, detail='Room not found')
    return room


@router.post('/paginated')
def read_paginated(
    pageParam: PaginationRequest,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    filter_dict: Dict[str, Any] = {}
    if pageParam.filters:
        filter_dict = pageParam.filters

    service = RoomService(db)
    total, items = service.get_paginated(
        page=pageParam.page,
        page_size=pageParam.page_size,
        filters=filter_dict,
        order_by=pageParam.order_by
    )
    return {
        "current_page": pageParam.page,
        "page_total": math.ceil(total / pageParam.page_size) if pageParam.page_size > 0 else 0,
        "total": total,
        "items": [RoomSchema.model_validate(item, from_attributes=True) for item in items]
    }
