from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CleanerSchema(BaseModel):
    id: int
    username: str
    full_name: str
    star_level: int
    total_orders: int
    total_rating: float
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class CleanerDetailSchema(BaseModel):
    id: int
    username: str
    full_name: str
    star_level: int
    total_orders: int
    total_rating: float
    avatar: Optional[str] = None
    recent_reviews: List[dict] = []

    class Config:
        from_attributes = True


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
    guest_name: str
    guest_phone: str
    scheduled_time: Optional[datetime] = None
    remarks: Optional[str] = None
    cleaner_id: Optional[int] = None


class PortalOrderSchema(BaseModel):
    order_id: int
    order_no: str
    status: int
    service_type_name: Optional[str] = None
    room_number: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    create_time: datetime
    price: Optional[float] = None

    class Config:
        from_attributes = True


class ServiceTypeDetailSchema(BaseModel):
    type_id: int
    type_name: str
    description: Optional[str] = None
    standard_time: int = 30
    price: float
    icon: Optional[str] = None
    features: List[str] = []
    process_steps: List[str] = []
    precautions: List[str] = []

    class Config:
        from_attributes = True


class CompanyInfoSchema(BaseModel):
    about_us: str = "CleanPro is a professional hotel cleaning service platform"
    phone: str = "400-888-8888"
    email: str = "service@cleanpro.com"
    address: str = "Pudong New District, Shanghai"
    facebook: str = ""
    twitter: str = ""
    instagram: str = ""

    class Config:
        from_attributes = True


class ReviewSchema(BaseModel):
    id: int
    guest_name: str
    rating: int
    comment: str
    service_type_name: Optional[str] = None
    create_time: str

    class Config:
        from_attributes = True


class CustomerRequirementSchema(BaseModel):
    id: int
    user_id: int
    guest_name: str
    guest_phone: str
    guest_email: Optional[str] = None
    property_type: str
    bedroom: int
    bathroom: int
    living_room: int
    kitchen: int
    lawn: int
    car_space: int
    square_footage: Optional[float] = None
    service_type_name: Optional[str] = None
    preferred_time: Optional[str] = None
    budget: Optional[float] = None
    description: Optional[str] = None
    status: int
    create_time: str

    class Config:
        from_attributes = True


class CleanerApplicationCreateSchema(BaseModel):
    requirement_id: int
    cleaner_id: int
    cleaner_name: str
    offered_price: Optional[float] = None
    message: Optional[str] = None


class CleanerApplicationSchema(BaseModel):
    id: int
    requirement_id: int
    cleaner_id: int
    cleaner_name: str
    offered_price: Optional[float] = None
    message: Optional[str] = None
    status: int
    star_level: Optional[int] = None
    total_orders: Optional[int] = None
    total_rating: Optional[float] = None
    create_time: str

    class Config:
        from_attributes = True


class CleanerTaskSchema(BaseModel):
    id: int
    task_type: str
    task_id: int
    title: str
    description: Optional[str] = None
    status: int
    status_text: str
    price: Optional[float] = None
    create_time: str
    update_time: Optional[str] = None

    class Config:
        from_attributes = True


class AdminRequirementSchema(BaseModel):
    id: int
    user_id: int
    guest_name: str
    guest_phone: str
    guest_email: Optional[str] = None
    property_type: str
    bedroom: int
    bathroom: int
    living_room: int
    kitchen: int
    lawn: int
    car_space: int
    square_footage: Optional[float] = None
    service_type_name: Optional[str] = None
    preferred_time: Optional[str] = None
    budget: Optional[float] = None
    description: Optional[str] = None
    status: int
    create_time: str
    applications_count: int = 0
    accepted_cleaner_id: Optional[int] = None
    accepted_cleaner_name: Optional[str] = None

    class Config:
        from_attributes = True


class AdminCleanerSchema(BaseModel):
    id: int
    username: str
    full_name: str
    star_level: int
    total_orders: int
    total_rating: float
    pending_tasks: int = 0
    completed_tasks: int = 0

    class Config:
        from_attributes = True
