from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.PaginationRequest import PaginationRequest
from core.dependencies import get_service
from service.role import role
from schemas.role import RoleSchema, RoleCreateSchema, RoleUpdateSchema

import math

# Database session and service dependencies

# Pydantic schemas for request and response validation

# Create API router with prefix and tag
router = APIRouter(prefix='/api/role', tags=['role'])

@router.get('/', response_model=List[RoleSchema])
def read_all(service: role = Depends(get_service(role))):
    """
    Retrieve all records.
    """
    return service.get_all()

@router.get('/{id}', response_model=RoleSchema)
def read_item(id, service: role = Depends(get_service(role))):
    """
    Retrieve a single record by primary key.
    """
    db_obj = service.get(id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return db_obj

@router.post('/', response_model=RoleSchema)
def create_item(item_in: RoleCreateSchema, service: role = Depends(get_service(role))):
    """
    Create a new record.
    """
    return service.create(item_in)

@router.put('/{id}', response_model=RoleSchema)
def update_item(id, item_in: RoleUpdateSchema, service: role = Depends(get_service(role))):
    """
    Update an existing record by primary key.
    """
    db_obj = service.get(id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    return service.update(db_obj, item_in)

@router.delete('/{id}')
def delete_item(id, service: role = Depends(get_service(role))):
    """
    Delete a record by primary key.
    """
    db_obj = service.get(id)
    if not db_obj:
        raise HTTPException(status_code=404, detail='Item not found')
    service.delete(db_obj)
    return {'ok': True}

@router.post('/paginated', response_model=Dict[str, Any])
def read_paginated(pageParam: PaginationRequest, service: role = Depends(get_service(role))):
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
        'items': [RoleSchema.model_validate(item, from_attributes=True) for item in items]
    }
