from sqlalchemy.orm import Session
from datetime import datetime
from cruds.CRUDBase import CRUDBase
from models.service_order import ServiceOrderModel
from models.user import UserModel
from schemas.housekeeping import ServiceOrderCreateSchema, ServiceOrderUpdateSchema
import random
import string


def generate_order_no():
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"SO{date_str}{random_str}"


class ServiceOrderCRUD(CRUDBase[ServiceOrderModel, ServiceOrderCreateSchema, ServiceOrderUpdateSchema]):
    pass


service_order_crud = ServiceOrderCRUD(ServiceOrderModel)


class ServiceOrderService:
    def __init__(self, db: Session):
        self.db = db

    def _enrich_with_staff_name(self, order: ServiceOrderModel) -> dict:
        order_dict = {
            'order_id': order.order_id,
            'order_no': order.order_no,
            'room_id': order.room_id,
            'guest_id': order.guest_id,
            'service_type_id': order.service_type_id,
            'assigned_staff_id': order.assigned_staff_id,
            'assigned_staff_name': None,
            'status': order.status,
            'priority': order.priority,
            'request_time': order.request_time,
            'scheduled_start': order.scheduled_start,
            'scheduled_end': order.scheduled_end,
            'actual_start': order.actual_start,
            'actual_complete': order.actual_complete,
            'remarks': order.remarks,
            'rating': order.rating,
            'create_time': order.create_time,
        }
        if order.assigned_staff_id:
            staff = self.db.query(UserModel).filter(UserModel.id == order.assigned_staff_id).first()
            if staff:
                order_dict['assigned_staff_name'] = staff.full_name
        return order_dict

    def get_all(self):
        orders = service_order_crud.get_all(self.db)
        return [self._enrich_with_staff_name(o) for o in orders]

    def get(self, id: int):
        order = service_order_crud.get(self.db, id)
        if order:
            return self._enrich_with_staff_name(order)
        return None

    def get(self, id: int):
        return service_order_crud.get(self.db, id)

    def get_by_cleaner(self, cleaner_id: int):
        orders = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.assigned_staff_id == cleaner_id,
            ServiceOrderModel.is_deleted == 0
        ).all()
        return [self._enrich_with_staff_name(o) for o in orders]

    def get_by_guest(self, guest_id: int):
        orders = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.guest_id == guest_id,
            ServiceOrderModel.is_deleted == 0
        ).all()
        return [self._enrich_with_staff_name(o) for o in orders]

    def create(self, obj_in: ServiceOrderCreateSchema, guest_id: int):
        data = obj_in.dict()
        data['order_no'] = generate_order_no()
        data['guest_id'] = guest_id
        data['status'] = 0
        obj = ServiceOrderModel(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._enrich_with_staff_name(obj)

    def update(self, id: int, obj_in: ServiceOrderUpdateSchema):
        db_obj = service_order_crud.get(self.db, id)
        if not db_obj:
            return None
        updated = service_order_crud.update(self.db, db_obj, obj_in)
        if updated:
            return self._enrich_with_staff_name(updated)
        return None

    def delete(self, id: int):
        db_obj = service_order_crud.get(self.db, id)
        if not db_obj:
            return False
        return service_order_crud.soft_delete(self.db, db_obj)

    def get_paginated(self, page: int = 1, page_size: int = 10, filters: dict = None, order_by: str = None):
        skip = (page - 1) * page_size
        total, items = service_order_crud.get_paginated(self.db, skip, page_size, filters, order_by)
        enriched_items = [self._enrich_with_staff_name(item) for item in items]
        return total, enriched_items

    def assign_staff(self, order_id: int, staff_id: int):
        from models.notification import NotificationModel
        order = service_order_crud.get(self.db, order_id)
        if not order:
            return None
        order.assigned_staff_id = staff_id
        order.status = 1
        self.db.commit()
        self.db.refresh(order)
        
        notification = NotificationModel(
            user_id=staff_id,
            title='New Task Assigned',
            content=f'You have been assigned order {order.order_no} for Room {order.room_id}',
            type='info',
            link_url='/orders'
        )
        self.db.add(notification)
        self.db.commit()
        
        return self._enrich_with_staff_name(order)

    def start_work(self, order_id: int):
        order = service_order_crud.get(self.db, order_id)
        if not order:
            return None
        order.status = 2
        order.actual_start = datetime.utcnow()
        self.db.commit()
        self.db.refresh(order)
        return self._enrich_with_staff_name(order)

    def complete(self, order_id: int):
        from models.notification import NotificationModel
        order = service_order_crud.get(self.db, order_id)
        if not order:
            return None
        order.status = 4
        order.actual_complete = datetime.utcnow()
        self.db.commit()
        self.db.refresh(order)
        
        notification = NotificationModel(
            user_id=order.guest_id,
            title='Order Completed',
            content=f'Your order {order.order_no} has been completed. Please rate the service.',
            type='success',
            link_url='/orders'
        )
        self.db.add(notification)
        self.db.commit()
        
        return self._enrich_with_staff_name(order)

    def cancel_order(self, order_id: int, reason: str = None):
        order = service_order_crud.get(self.db, order_id)
        if not order:
            return None
        order.status = 5
        if reason:
            order.remarks = (order.remarks or '') + f' [Cancelled: {reason}]'
        self.db.commit()
        self.db.refresh(order)
        return self._enrich_with_staff_name(order)

    def rate_order(self, order_id: int, rating: int, comment: str = None):
        order = service_order_crud.get(self.db, order_id)
        if not order:
            return None
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        order.rating = rating
        if comment:
            order.guest_feedback = comment
        self.db.commit()
        self.db.refresh(order)
        return self._enrich_with_staff_name(order)

    def upload_photo(self, order_id: int, photo_type: str, photo_data: str):
        order = service_order_crud.get(self.db, order_id)
        if not order:
            return None
        if photo_type == 'before':
            order.before_photo = photo_data
        elif photo_type == 'after':
            order.after_photo = photo_data
        self.db.commit()
        self.db.refresh(order)
        return self._enrich_with_staff_name(order)
