from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import random
import string

from database import get_db
from models.user import UserModel
from models.service_type import ServiceTypeModel
from models.room import RoomModel
from models.service_order import ServiceOrderModel


router = APIRouter(prefix='/api/portal', tags=['portal'])


class PortalServiceTypeSchema(BaseModel):
    type_id: int
    type_name: str
    description: Optional[str] = None
    standard_time: int = 30
    price: float
    icon: Optional[str] = None

    class Config:
        from_attributes = True


class PortalRoomSchema(BaseModel):
    room_id: int
    room_number: str
    room_type: str
    floor: int
    price: float
    status: int
    image_url: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class PortalOrderCreateSchema(BaseModel):
    service_type_id: int
    room_id: int
    guest_name: str
    guest_phone: str
    scheduled_time: Optional[datetime] = None
    remarks: Optional[str] = None


class PortalOrderSchema(BaseModel):
    order_id: int
    order_no: str
    status: int
    service_type_name: Optional[str] = None
    room_number: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    create_time: datetime

    class Config:
        from_attributes = True


@router.get('/services', response_model=List[PortalServiceTypeSchema])
def get_portal_services(db: Session = Depends(get_db)):
    """Get all active service types for portal display"""
    services = db.query(ServiceTypeModel).filter(
        ServiceTypeModel.is_deleted == 0,
        ServiceTypeModel.is_active == 1
    ).all()
    
    icons = ['House', 'Brush', 'Key', 'OfficeBuilding', 'Document', 'Sunny', 'Calendar', 'Timer']
    
    result = []
    for i, s in enumerate(services):
        result.append(PortalServiceTypeSchema(
            type_id=s.type_id,
            type_name=s.type_name,
            description=s.description,
            standard_time=s.standard_time,
            price=float(s.price),
            icon=icons[i % len(icons)]
        ))
    
    if not result:
        result = [
            PortalServiceTypeSchema(type_id=1, type_name='房间清洁', description='专业房间打扫整理', standard_time=30, price=68, icon='House'),
            PortalServiceTypeSchema(type_id=2, type_name='深度清洁', description='全面深度清洁服务', standard_time=60, price=168, icon='Brush'),
            PortalServiceTypeSchema(type_id=3, type_name='开荒保洁', description='新居入住前清洁', standard_time=120, price=288, icon='Key'),
            PortalServiceTypeSchema(type_id=4, type_name='办公室清洁', description='办公环境维护', standard_time=45, price=128, icon='OfficeBuilding'),
            PortalServiceTypeSchema(type_id=5, type_name='布草更换', description='床品换洗服务', standard_time=20, price=38, icon='Document'),
            PortalServiceTypeSchema(type_id=6, type_name='玻璃清洁', description='门窗玻璃擦拭', standard_time=30, price=58, icon='Sunny'),
        ]
    
    return result


@router.get('/rooms', response_model=List[PortalRoomSchema])
def get_portal_rooms(db: Session = Depends(get_db)):
    """Get available rooms for portal display"""
    rooms = db.query(RoomModel).filter(
        RoomModel.is_deleted == 0,
        RoomModel.status == 1
    ).limit(20).all()
    
    if not rooms:
        rooms = [
            RoomModel(room_id=1, room_number='101', floor=1, room_type='标准间', price=199, status=1, description='舒适标准间'),
            RoomModel(room_id=2, room_number='102', floor=1, room_type='标准间', price=199, status=1, description='舒适标准间'),
            RoomModel(room_id=3, room_number='201', floor=2, room_type='豪华间', price=399, status=1, description='豪华大床房'),
            RoomModel(room_id=4, room_number='202', floor=2, room_type='豪华间', price=399, status=1, description='豪华大床房'),
            RoomModel(room_id=5, room_number='301', floor=3, room_type='套房', price=599, status=1, description='豪华套房'),
        ]
    
    return rooms


def generate_order_no():
    """Generate order number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f'JDW{timestamp}{random_str}'


@router.post('/order')
def create_portal_order(
    order: PortalOrderCreateSchema,
    db: Session = Depends(get_db)
):
    """Create a new service order from portal"""
    service_type = db.query(ServiceTypeModel).filter(
        ServiceTypeModel.type_id == order.service_type_id,
        ServiceTypeModel.is_deleted == 0
    ).first()
    
    if not service_type:
        raise HTTPException(status_code=404, detail='Service type not found')
    
    room = db.query(RoomModel).filter(
        RoomModel.room_id == order.room_id,
        RoomModel.is_deleted == 0
    ).first()
    
    if not room:
        raise HTTPException(status_code=404, detail='Room not found')
    
    guest = db.query(UserModel).filter(
        UserModel.phone == order.guest_phone,
        UserModel.is_deleted == 0
    ).first()
    
    if not guest:
        guest = UserModel(
            username=order.guest_phone,
            full_name=order.guest_name,
            phone=order.guest_phone,
            role='guest',
            status=1
        )
        guest.set_password('guest123')
        db.add(guest)
        db.commit()
        db.refresh(guest)
    
    scheduled_time = order.scheduled_time or datetime.now()
    
    new_order = ServiceOrderModel(
        order_no=generate_order_no(),
        room_id=order.room_id,
        guest_id=guest.id,
        service_type_id=order.service_type_id,
        status=0,
        priority=0,
        request_time=datetime.now(),
        scheduled_start=scheduled_time,
        remarks=order.remarks
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    return {
        'success': True,
        'order_id': new_order.order_id,
        'order_no': new_order.order_no,
        'message': 'Order created successfully'
    }


@router.get('/orders/{phone}', response_model=List[PortalOrderSchema])
def get_portal_orders(
    phone: str,
    db: Session = Depends(get_db)
):
    """Get orders by phone number"""
    guest = db.query(UserModel).filter(
        UserModel.phone == phone,
        UserModel.is_deleted == 0
    ).first()
    
    if not guest:
        return []
    
    orders = db.query(ServiceOrderModel).filter(
        ServiceOrderModel.guest_id == guest.id,
        ServiceOrderModel.is_deleted == 0
    ).order_by(ServiceOrderModel.create_time.desc()).limit(50).all()
    
    result = []
    for order in orders:
        service_type = db.query(ServiceTypeModel).filter(ServiceTypeModel.type_id == order.service_type_id).first()
        room = db.query(RoomModel).filter(RoomModel.room_id == order.room_id).first()
        
        result.append(PortalOrderSchema(
            order_id=order.order_id,
            order_no=order.order_no,
            status=order.status,
            service_type_name=service_type.type_name if service_type else None,
            room_number=room.room_number if room else None,
            scheduled_start=order.scheduled_start,
            create_time=order.create_time
        ))
    
    return result


@router.get('/stats')
def get_portal_stats(db: Session = Depends(get_db)):
    """Get portal statistics"""
    total_users = db.query(UserModel).filter(UserModel.is_deleted == 0).count()
    total_orders = db.query(ServiceOrderModel).filter(ServiceOrderModel.is_deleted == 0).count()
    total_rooms = db.query(RoomModel).filter(RoomModel.is_deleted == 0, RoomModel.status == 1).count()
    
    return {
        'total_users': total_users,
        'total_orders': total_orders,
        'total_rooms': total_rooms,
        'rating': 4.9
    }
