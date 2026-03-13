from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.dependencies import get_current_user, require_permission, get_service
from service.service_type import ServiceTypeService
from model.user import UserModel
from schemas.housekeeping import ServiceTypeSchema, ServiceTypeCreateSchema




router = APIRouter(prefix='/api/service-type', tags=['service-type'])


@router.get('/', response_model=List[ServiceTypeSchema])
def get_all(
    current_user: UserModel = Depends(require_permission()),
    service: ServiceTypeService = Depends(get_service(ServiceTypeService))
):
    return service.get_all()


@router.get('/{type_id}', response_model=ServiceTypeSchema)
def get_item(
    type_id: int,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceTypeService = Depends(get_service(ServiceTypeService))
):
    item = service.get(type_id)
    if not item:
        raise HTTPException(status_code=404, detail='Service type not found')
    return item


@router.post('/', response_model=ServiceTypeSchema)
def create_item(
    item_in: ServiceTypeCreateSchema,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceTypeService = Depends(get_service(ServiceTypeService))
):
    return service.create(
        type_name=item_in.type_name,
        description=item_in.description,
        standard_time=item_in.standard_time,
        price=item_in.price
    )


@router.put('/{type_id}', response_model=ServiceTypeSchema)
def update_item(
    type_id: int,
    item_in: dict,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceTypeService = Depends(get_service(ServiceTypeService))
):
    item = service.update(type_id, item_in)
    if not item:
        raise HTTPException(status_code=404, detail='Service type not found')
    return item


@router.delete('/{type_id}')
def delete_item(
    type_id: int,
    current_user: UserModel = Depends(require_permission()),
    service: ServiceTypeService = Depends(get_service(ServiceTypeService))
):
    item = service.delete(type_id)
    if not item:
        raise HTTPException(status_code=404, detail='Service type not found')
    return {'ok': True}
