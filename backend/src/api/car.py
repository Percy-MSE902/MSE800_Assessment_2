from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.PaginationRequest import PaginationRequest
from core.dependencies import get_service
from service.car import car
from schemas.car import CarSchema, CarCreateSchema, CarUpdateSchema

import math

# Database session and service dependencies

# Pydantic schemas for request and response validation

# Create API router with prefix and tag
router = APIRouter(prefix='/api/car', tags=['car'])

@router.get('/', response_model=List[CarSchema])
def read_all(service: car = Depends(get_service(car))):
    """
    Retrieve all records.
    """
    return service.get_all()

@router.get('/{car_id}', response_model=CarSchema)
def read_item(car_id, service: car = Depends(get_service(car))):
    """
    Retrieve a single record by primary key.
    """
    db_obj = service.get(car_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return db_obj

@router.post('/', response_model=CarSchema)
def create_item(item_in: CarCreateSchema, service: car = Depends(get_service(car))):
    """
    Create a new record.
    """
    return service.create(item_in)

@router.put('/{car_id}', response_model=CarSchema)
def update_item(car_id, item_in: CarUpdateSchema, service: car = Depends(get_service(car))):
    """
    Update an existing record by primary key.
    """
    db_obj = service.get(car_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return service.update(db_obj, item_in)

@router.delete('/{car_id}')
def delete_item(car_id, service: car = Depends(get_service(car))):
    """
    Delete a record by primary key.
    """
    db_obj = service.get(car_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    service.delete(db_obj)
    return {'ok': True}

@router.post('/paginated', response_model=Dict[str, Any])
def read_paginated(pageParam: PaginationRequest, service: car = Depends(get_service(car))):
    """
    Paginated list of records with optional filters and sorting.
    """
    filter_dict: Dict[str, Any] = {}
    if pageParam.filters:
        try:
            filter_dict = pageParam.filters
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid filters JSON")

    total, items = service.get_paginated(
        page=pageParam.page,
        page_size=pageParam.page_size,
        filters=filter_dict,
        order_by=pageParam.order_by
    )
    return {
        'current_page': pageParam.page,
        'page_total': math.ceil(total / pageParam.page_size),
        'total': total,
        'items': [CarSchema.model_validate(item, from_attributes=True) for item in items]
    }
