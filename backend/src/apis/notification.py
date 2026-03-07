from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import math

from database import get_db
from models.user import UserModel
from models.notification import NotificationModel
from core.dependencies import get_current_user, require_permission


router = APIRouter(prefix='/api/notification', tags=['notification'])


class NotificationSchema(BaseModel):
    id: Optional[int] = None
    user_id: int
    title: str
    content: Optional[str] = None
    type: str = 'info'
    link_url: Optional[str] = None
    is_read: int = 0
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationCreateSchema(BaseModel):
    user_id: int
    title: str
    content: Optional[str] = None
    type: str = 'info'
    link_url: Optional[str] = None


@router.get('/paginated')
def get_notifications_paginated(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    type: Optional[str] = Query(None),
    is_read: Optional[int] = Query(None),
    title: Optional[str] = Query(None),
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    query = db.query(NotificationModel).filter(NotificationModel.user_id == current_user.id)
    
    if type:
        query = query.filter(NotificationModel.type == type)
    if is_read is not None:
        query = query.filter(NotificationModel.is_read == is_read)
    if title:
        query = query.filter(NotificationModel.title.like(f'%{title}%'))
    
    total = query.count()
    items = query.order_by(NotificationModel.create_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "current_page": page,
        "page_total": math.ceil(total / page_size) if page_size > 0 else 0,
        "total": total,
        "items": [NotificationSchema.model_validate(item, from_attributes=True) for item in items]
    }


@router.get('/', response_model=List[NotificationSchema])
def get_notifications(
    unread_only: bool = False,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    query = db.query(NotificationModel).filter(NotificationModel.user_id == current_user.id)
    if unread_only:
        query = query.filter(NotificationModel.is_read == 0)
    return query.order_by(NotificationModel.create_time.desc()).limit(50).all()


@router.get('/unread-count')
def get_unread_count(
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    count = db.query(NotificationModel).filter(
        NotificationModel.user_id == current_user.id,
        NotificationModel.is_read == 0
    ).count()
    return {'count': count}


@router.post('/{notification_id}/read')
def mark_as_read(
    notification_id: int,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    notification = db.query(NotificationModel).filter(
        NotificationModel.id == notification_id,
        NotificationModel.user_id == current_user.id
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail='Notification not found')
    notification.is_read = 1
    db.commit()
    return {'ok': True}


@router.post('/read-all')
def mark_all_as_read(
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    db.query(NotificationModel).filter(
        NotificationModel.user_id == current_user.id,
        NotificationModel.is_read == 0
    ).update({'is_read': 1})
    db.commit()
    return {'ok': True}


@router.delete('/{notification_id}')
def delete_notification(
    notification_id: int,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    notification = db.query(NotificationModel).filter(
        NotificationModel.id == notification_id,
        NotificationModel.user_id == current_user.id
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail='Notification not found')
    db.delete(notification)
    db.commit()
    return {'ok': True}


@router.post('/create')
def create_notification(
    notification_in: NotificationCreateSchema,
    db: Session = Depends(get_db)
):
    notification = NotificationModel(**notification_in.dict())
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
