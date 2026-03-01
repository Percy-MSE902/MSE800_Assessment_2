from pydantic import BaseModel, ConfigDict
from datetime import datetime, date, time
from typing import Optional


class UserSchema(BaseModel):
    id: Optional[int] = None
    username: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = 'guest'
    status: int = 1
    create_time: Optional[datetime] = None
    modify_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreateSchema(BaseModel):
    username: str
    password: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = 'guest'


class UserUpdateSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    status: Optional[int] = None


class RoomSchema(BaseModel):
    room_id: Optional[int] = None
    room_number: str
    floor: int
    room_type: str
    capacity: int = 2
    price: float
    status: int = 0
    last_clean_time: Optional[datetime] = None
    description: Optional[str] = None
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoomCreateSchema(BaseModel):
    room_number: str
    floor: int
    room_type: str
    capacity: int = 2
    price: float
    description: Optional[str] = None


class RoomUpdateSchema(BaseModel):
    room_type: Optional[str] = None
    capacity: Optional[int] = None
    price: Optional[float] = None
    status: Optional[int] = None
    description: Optional[str] = None


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


class ServiceOrderSchema(BaseModel):
    order_id: Optional[int] = None
    order_no: Optional[str] = None
    room_id: int
    guest_id: int
    service_type_id: int
    assigned_staff_id: Optional[int] = None
    assigned_staff_name: Optional[str] = None
    status: int = 0
    priority: int = 0
    request_time: datetime
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_complete: Optional[datetime] = None
    before_photo: Optional[str] = None
    after_photo: Optional[str] = None
    remarks: Optional[str] = None
    rating: Optional[int] = None
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class ServiceOrderCreateSchema(BaseModel):
    room_id: int
    service_type_id: int
    priority: int = 0
    request_time: datetime
    remarks: Optional[str] = None


class ServiceOrderUpdateSchema(BaseModel):
    assigned_staff_id: Optional[int] = None
    status: Optional[int] = None
    scheduled_start: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_complete: Optional[datetime] = None
    before_photo: Optional[str] = None
    after_photo: Optional[str] = None
    remarks: Optional[str] = None


class OrderPhotoSchema(BaseModel):
    id: Optional[int] = None
    order_id: int
    photo_type: str
    photo_url: str
    description: Optional[str] = None
    uploaded_by: Optional[int] = None
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderPhotoCreateSchema(BaseModel):
    order_id: int
    photo_type: str
    photo_url: str
    description: Optional[str] = None


class InspectionSchema(BaseModel):
    inspection_id: Optional[int] = None
    order_id: int
    inspector_id: int
    cleaner_id: int
    status: int = 0
    score: Optional[int] = None
    issues: Optional[str] = None
    inspection_time: datetime

    class Config:
        from_attributes = True


class InventoryItemSchema(BaseModel):
    item_id: Optional[int] = None
    item_name: str
    category: str
    quantity: int
    min_stock: int
    unit: str
    location: Optional[str] = None
    is_active: int = 1

    class Config:
        from_attributes = True


class InventoryItemCreateSchema(BaseModel):
    item_name: str
    category: str
    quantity: int = 0
    min_stock: int = 10
    unit: str
    location: Optional[str] = None


class ReviewSchema(BaseModel):
    review_id: Optional[int] = None
    order_id: int
    rating: int
    comment: Optional[str] = None

    class Config:
        from_attributes = True


class ReviewCreateSchema(BaseModel):
    order_id: int
    rating: int
    comment: Optional[str] = None
