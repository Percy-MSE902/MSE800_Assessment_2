# Standard library imports
import random
from datetime import datetime
from typing import List, Optional

# Third-party imports
from sqlalchemy.orm import Session

# Local application imports
from model.cleaner_application import CleanerApplicationModel
from model.customer_requirement import CustomerRequirementModel
from model.room import RoomModel
from model.service_order import ServiceOrderModel
from model.service_type import ServiceTypeModel
from model.user import UserModel


class PortalService:
    """Service class for portal-related operations."""

    def __init__(self, db: Session):
        """Initialize the service with database session."""
        self.db = db

    # pylint: disable=too-many-branches
    def get_all_service_types(self) -> List[ServiceTypeModel]:
        """Get all active service types.

        Returns:
            List of active ServiceTypeModel objects.
        """
        return self.db.query(ServiceTypeModel).filter(
            ServiceTypeModel.is_deleted == 0,
            ServiceTypeModel.is_active == 1
        ).all()

    def get_service_type_detail(self, type_id: int) -> dict:
        """Get service type detail with features, process steps, precautions.

        Args:
            type_id: The ID of the service type.

        Returns:
            Dictionary containing service type details.
        """
        service = self.db.query(ServiceTypeModel).filter(
            ServiceTypeModel.type_id == type_id,
            ServiceTypeModel.is_deleted == 0,
            ServiceTypeModel.is_active == 1
        ).first()

        if not service:
            return {
                'type_id': type_id,
                'type_name': 'Service',
                'description': 'Service details',
                'standard_time': 30,
                'price': 0,
                'icon': 'House',
                'features': ['Professional service'],
                'process_steps': ['Book', 'Confirm', 'Service', 'Complete'],
                'precautions': ['Follow guidelines']
            }

        icons = ['House', 'OfficeBuilding', 'Grid', 'Brush', 'Cpu', 'Shop', 'Delete', 'Cloudy', 'Monitor', 'FirstAidKit', 'Key']

        features_map = {
            'Regular Cleaning': ['Dust removal', 'Bed making', 'Floor vacuuming', 'Bathroom cleaning', 'Trash disposal'],
            'Deep Cleaning': ['All regular cleaning tasks', 'Interior appliance cleaning', 'Window cleaning', 'Tile grout cleaning', 'Air vent cleaning'],
            'Bed Sheet Change': ['Fresh linen installation', 'Pillowcase change', 'Bedspread refresh', 'Mattress rotation'],
            'Express Cleaning': ['Quick tidy up', 'Surface cleaning', 'Bathroom refresh', 'Floor sweep'],
            'Home Cleaning': ['Full home cleaning', 'Kitchen deep clean', 'Bathroom sanitization', 'Living areas cleaning'],
            'Commercial Cleaning': ['Office space cleaning', 'Conference room cleaning', 'Reception area', 'Restroom sanitization'],
        }

        process_map = {
            'Regular Cleaning': ['Book appointment', 'Cleaner arrives', 'Service execution', 'Quality check', 'Payment'],
            'Deep Cleaning': ['Assessment', 'Deep clean all areas', 'Specialized cleaning', 'Final inspection', 'Customer sign-off'],
            'Bed Sheet Change': ['Book appointment', 'Remove old linen', 'Install fresh linen', 'Quality check'],
            'Express Cleaning': ['Quick booking', 'Rapid service', 'Quick review', 'Done'],
        }

        precautions_map = {
            'Regular Cleaning': ['Please remove valuables', 'Keep pets away during cleaning', 'Ensure someone is home'],
            'Deep Cleaning': ['Clear access to all areas', 'Remove fragile items', 'Ventilate the space'],
            'Bed Sheet Change': ['Provide linen preference', 'Inform of bed size', 'Any special instructions'],
            'Express Cleaning': ['Focus on main areas', 'Quick turnaround', 'Basic cleaning only'],
        }

        features = features_map.get(service.type_name, ['Professional service', 'Experienced cleaners', 'Quality guarantee', 'Satisfaction insured'])
        process_steps = process_map.get(service.type_name, ['Book', 'Confirm', 'Service', 'Complete'])
        precautions = precautions_map.get(service.type_name, ['Follow guidelines', 'Ensure access', 'Supervise if needed'])

        return {
            'type_id': service.type_id,
            'type_name': service.type_name,
            'description': service.description,
            'standard_time': service.standard_time,
            'price': float(service.price),
            'icon': icons[service.type_id % len(icons)] if service.type_id else 'House',
            'features': features,
            'process_steps': process_steps,
            'precautions': precautions
        }

    def get_all_rooms(self) -> List[RoomModel]:
        """Get all active rooms"""
        return self.db.query(RoomModel).filter(
            RoomModel.is_deleted == 0,
            RoomModel.status == 1
        ).all()

    def create_order(self, order_data: dict) -> dict:
        """Create a new order"""
        guest = self.db.query(UserModel).filter(
            UserModel.phone == order_data.get('guest_phone'),
            UserModel.is_deleted == 0
        ).first()

        if not guest:
            return {'success': False, 'message': 'User not found'}

        service_type = self.db.query(ServiceTypeModel).filter(
            ServiceTypeModel.type_id == order_data.get('service_type_id'),
            ServiceTypeModel.is_deleted == 0
        ).first()

        if not service_type:
            return {'success': False, 'message': 'Service type not found'}

        order_no = f"SO{datetime.now().strftime('%Y%m%d%H%M')}{random.randint(100, 999)}"

        new_order = ServiceOrderModel(
            order_no=order_no,
            guest_id=guest.id,
            service_type_id=order_data.get('service_type_id'),
            assigned_staff_id=order_data.get('cleaner_id'),
            status=0,
            priority=0,
            request_time=datetime.now(),
            scheduled_start=order_data.get('scheduled_time') if order_data.get('scheduled_time') else None,
            remarks=order_data.get('remarks'),
            create_time=datetime.now(),
            modify_time=datetime.now()
        )

        self.db.add(new_order)
        self.db.commit()

        return {'success': True, 'order_no': order_no, 'order_id': new_order.order_id}

    def get_orders_by_phone(self, phone: str) -> List[dict]:
        """Get orders by phone number"""
        guest = self.db.query(UserModel).filter(
            UserModel.phone == phone,
            UserModel.is_deleted == 0
        ).first()

        if not guest:
            return []

        orders = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.guest_id == guest.id,
            ServiceOrderModel.is_deleted == 0
        ).order_by(ServiceOrderModel.create_time.desc()).all()

        result = []
        for order in orders:
            service_type = self.db.query(ServiceTypeModel).filter(
                ServiceTypeModel.type_id == order.service_type_id
            ).first()

            result.append({
                'order_id': order.order_id,
                'order_no': order.order_no,
                'status': order.status,
                'service_type_name': service_type.type_name if service_type else None,
                'scheduled_start': order.scheduled_start,
                'create_time': order.create_time,
                'price': float(service_type.price) if service_type else 0,
                'actual_price': float(service_type.price) if service_type else 0
            })

        return result

    def get_stats(self) -> dict:
        """Get portal statistics"""
        total_users = self.db.query(UserModel).filter(UserModel.is_deleted == 0).count()

        completed_orders = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.is_deleted == 0,
            ServiceOrderModel.status == 4
        ).count()

        total_rooms = self.db.query(RoomModel).filter(
            RoomModel.is_deleted == 0,
            RoomModel.status == 1
        ).count()

        ratings = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.is_deleted == 0,
            ServiceOrderModel.rating.isnot(None)
        ).all()

        avg_rating = 4.9
        if ratings:
            total_rating = sum([r.rating for r in ratings])
            avg_rating = round(total_rating / len(ratings), 1)

        return {
            'total_users': total_users,
            'total_orders': completed_orders,
            'total_rooms': total_rooms,
            'rating': avg_rating
        }

    def get_company_info(self) -> dict:
        """Get company info"""
        return {
            'about_us': 'CleanPro is a professional hotel cleaning service platform, committed to providing high-quality cleaning services to our customers.',
            'phone': '400-888-8888',
            'email': 'service@cleanpro.com',
            'address': 'Pudong New District, Shanghai',
            'facebook': '',
            'twitter': '',
            'instagram': ''
        }

    def get_reviews(self, limit: int = 10, offset: int = 0) -> List[dict]:
        """Get customer reviews"""
        reviews = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.is_deleted == 0,
            ServiceOrderModel.guest_feedback.isnot(None),
            ServiceOrderModel.rating.isnot(None)
        ).order_by(ServiceOrderModel.create_time.desc()).offset(offset).limit(limit).all()

        result = []
        for r in reviews:
            service_type = self.db.query(ServiceTypeModel).filter(
                ServiceTypeModel.type_id == r.service_type_id
            ).first()
            guest = self.db.query(UserModel).filter(UserModel.id == r.guest_id).first()

            result.append({
                'id': r.order_id,
                'guest_name': guest.full_name if guest and guest.full_name else 'Guest',
                'rating': int(r.rating) if r.rating else 5,
                'comment': r.guest_feedback or 'Great service!',
                'service_type_name': service_type.type_name if service_type else 'Cleaning Service',
                'create_time': r.create_time.strftime('%Y-%m-%d') if r.create_time else ''
            })

        if not result:
            result = [
                {'id': 1, 'guest_name': 'John D.', 'rating': 5, 'comment': 'Excellent service!', 'service_type_name': 'Deep Cleaning', 'create_time': '2026-03-10'},
                {'id': 2, 'guest_name': 'Sarah M.', 'rating': 5, 'comment': 'Highly recommend!', 'service_type_name': 'Regular Cleaning', 'create_time': '2026-03-09'},
            ]

        return result

    def get_reviews_count(self) -> dict:
        """Get total reviews count"""
        count = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.is_deleted == 0,
            ServiceOrderModel.guest_feedback.isnot(None),
            ServiceOrderModel.rating.isnot(None)
        ).count()
        return {'total': count}

    def get_review_detail(self, review_id: int) -> dict:
        """Get single review detail"""
        order = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.order_id == review_id,
            ServiceOrderModel.is_deleted == 0
        ).first()

        if not order or not order.guest_feedback:
            raise ValueError('Review not found')

        service_type = self.db.query(ServiceTypeModel).filter(
            ServiceTypeModel.type_id == order.service_type_id
        ).first()
        guest = self.db.query(UserModel).filter(UserModel.id == order.guest_id).first()

        return {
            'id': order.order_id,
            'guest_name': guest.full_name if guest and guest.full_name else 'Guest',
            'rating': int(order.rating) if order.rating else 5,
            'comment': order.guest_feedback or 'Great service!',
            'service_type_name': service_type.type_name if service_type else 'Cleaning Service',
            'create_time': order.create_time.strftime('%Y-%m-%d') if order.create_time else ''
        }

    def get_all_cleaners(self, sort_by: str = None, search: str = None) -> List[dict]:
        """Get all active cleaners with optional sorting and filtering"""
        query = self.db.query(UserModel).filter(
            UserModel.role.in_(['staff', 'cleaner', 'employee']),
            UserModel.is_deleted == 0,
            UserModel.status == 1
        )

        if search:
            query = query.filter(UserModel.full_name.ilike(f'%{search}%'))

        cleaners = query.all()

        result = []
        for c in cleaners:
            result.append({
                'id': c.id,
                'username': c.username,
                'full_name': c.full_name or c.username,
                'star_level': c.star_level or 1,
                'total_orders': c.total_orders or 0,
                'total_rating': round(c.total_rating or 5.0, 1),
                'distance': None,
                'avatar': None
            })

        if sort_by == 'rating_desc':
            result.sort(key=lambda x: x['total_rating'], reverse=True)
        elif sort_by == 'rating_asc':
            result.sort(key=lambda x: x['total_rating'])
        elif sort_by == 'orders_desc':
            result.sort(key=lambda x: x['total_orders'], reverse=True)
        elif sort_by == 'orders_asc':
            result.sort(key=lambda x: x['total_orders'])

        return result

    def get_cleaner_detail(self, cleaner_id: int) -> dict:
        """Get cleaner detail with recent reviews"""
        cleaner = self.db.query(UserModel).filter(
            UserModel.id == cleaner_id,
            UserModel.is_deleted == 0
        ).first()

        if not cleaner:
            raise ValueError('Cleaner not found')

        return {
            'id': cleaner.id,
            'username': cleaner.username,
            'full_name': cleaner.full_name or cleaner.username,
            'star_level': cleaner.star_level or 1,
            'total_orders': cleaner.total_orders or 0,
            'total_rating': cleaner.total_rating or 5.0,
            'avatar': None,
            'recent_reviews': []
        }

    def get_cleaner_applications(self, cleaner_id: int) -> List[dict]:
        """Get all applications for a cleaner"""
        result = []

        applications = self.db.query(CleanerApplicationModel).filter(
            CleanerApplicationModel.cleaner_id == cleaner_id,
            CleanerApplicationModel.is_deleted == 0
        ).order_by(CleanerApplicationModel.create_time.desc()).all()

        status_text_map = {0: 'Pending', 1: 'Accepted', 2: 'Rejected', 3: 'Completed'}

        for app in applications:
            requirement = self.db.query(CustomerRequirementModel).filter(
                CustomerRequirementModel.id == app.requirement_id
            ).first()

            result.append({
                'id': app.id,
                'task_type': 'application',
                'task_id': app.requirement_id,
                'title': f"Application for: {requirement.property_type if requirement else 'Requirement'}",
                'description': f"Budget: ${app.offered_price}" + (f", Message: {app.message}" if app.message else ""),
                'status': app.status,
                'status_text': status_text_map.get(app.status, 'Unknown'),
                'price': app.offered_price,
                'create_time': app.create_time.strftime('%Y-%m-%d %H:%M') if app.create_time else '',
                'update_time': app.create_time.strftime('%Y-%m-%d %H:%M') if app.create_time else ''
            })

        orders = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.assigned_staff_id == cleaner_id,
            ServiceOrderModel.is_deleted == 0,
            ServiceOrderModel.status.in_([3, 4])
        ).order_by(ServiceOrderModel.create_time.desc()).all()

        for order in orders:
            service_type = self.db.query(ServiceTypeModel).filter(
                ServiceTypeModel.type_id == order.service_type_id
            ).first()

            result.append({
                'id': order.order_id,
                'task_type': 'order',
                'task_id': order.order_id,
                'title': f"Order #{order.order_no}: {service_type.type_name if service_type else 'Service'}",
                'description': f"Order for {order.order_no}",
                'status': order.status,
                'status_text': 'Completed' if order.status == 4 else 'In Progress',
                'price': float(service_type.price) if service_type else 0,
                'create_time': order.create_time.strftime('%Y-%m-%d %H:%M') if order.create_time else '',
                'update_time': order.actual_complete.strftime('%Y-%m-%d %H:%M') if order.actual_complete else ''
            })

        return result

    def get_cleaner_applications(self, cleaner_id: int) -> List[dict]:
        """Get all applications by a cleaner"""
        applications = self.db.query(CleanerApplicationModel).filter(
            CleanerApplicationModel.cleaner_id == cleaner_id,
            CleanerApplicationModel.is_deleted == 0
        ).order_by(CleanerApplicationModel.create_time.desc()).all()

        result = []
        for app in applications:
            result.append({
                'id': app.id,
                'requirement_id': app.requirement_id,
                'cleaner_id': app.cleaner_id,
                'cleaner_name': app.cleaner_name,
                'offered_price': app.offered_price,
                'message': app.message,
                'status': app.status,
                'star_level': None,
                'total_orders': None,
                'total_rating': None,
                'create_time': app.create_time.strftime('%Y-%m-%d %H:%M') if app.create_time else ''
            })

        return result

    def get_all_requirements(self, limit: int = 50) -> List[dict]:
        """Get all requirements that are not yet assigned to a cleaner"""
        requirements = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.is_deleted == 0,
            CustomerRequirementModel.assigned_cleaner_id == None
        ).order_by(CustomerRequirementModel.create_time.desc()).limit(limit).all()

        result = []
        for req in requirements:
            result.append({
                'id': req.id,
                'user_id': req.user_id,
                'guest_name': req.guest_name,
                'guest_phone': req.guest_phone,
                'guest_email': req.guest_email,
                'property_type': req.property_type,
                'bedroom': req.bedroom,
                'bathroom': req.bathroom,
                'living_room': req.living_room,
                'kitchen': req.kitchen,
                'lawn': req.lawn,
                'car_space': req.car_space,
                'square_footage': req.square_footage,
                'service_type_name': req.service_type_name,
                'preferred_time': req.preferred_time,
                'budget': req.budget,
                'description': req.description,
                'status': req.status,
                'assigned_cleaner_id': req.assigned_cleaner_id,
                'create_time': req.create_time.strftime('%Y-%m-%d %H:%M') if req.create_time else ''
            })

        return result

    def get_requirements_by_phone(self, phone: str) -> List[dict]:
        """Get requirements by phone"""
        requirements = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.guest_phone == phone,
            CustomerRequirementModel.is_deleted == 0
        ).order_by(CustomerRequirementModel.create_time.desc()).all()

        result = []
        for req in requirements:
            result.append({
                'id': req.id,
                'user_id': req.user_id,
                'guest_name': req.guest_name,
                'guest_phone': req.guest_phone,
                'guest_email': req.guest_email,
                'property_type': req.property_type,
                'bedroom': req.bedroom,
                'bathroom': req.bathroom,
                'living_room': req.living_room,
                'kitchen': req.kitchen,
                'lawn': req.lawn,
                'car_space': req.car_space,
                'square_footage': req.square_footage,
                'service_type_name': req.service_type_name,
                'preferred_time': req.preferred_time,
                'budget': req.budget,
                'description': req.description,
                'status': req.status,
                'assigned_cleaner_id': req.assigned_cleaner_id,
                'create_time': req.create_time.strftime('%Y-%m-%d %H:%M') if req.create_time else ''
            })

        return result

    def create_requirement(self, requirement_data: dict) -> dict:
        """Create a new customer requirement"""
        guest = self.db.query(UserModel).filter(
            UserModel.phone == requirement_data.get('guest_phone'),
            UserModel.is_deleted == 0
        ).first()

        if not guest:
            return {'success': False, 'message': 'User not found'}

        new_req = CustomerRequirementModel(
            user_id=guest.id,
            guest_name=requirement_data.get('guest_name'),
            guest_phone=requirement_data.get('guest_phone'),
            guest_email=requirement_data.get('guest_email'),
            property_type=requirement_data.get('property_type'),
            bedroom=requirement_data.get('bedroom', 1),
            bathroom=requirement_data.get('bathroom', 1),
            living_room=requirement_data.get('living_room', 1),
            kitchen=requirement_data.get('kitchen', 0),
            lawn=requirement_data.get('lawn', 0),
            car_space=requirement_data.get('car_space', 0),
            square_footage=requirement_data.get('square_footage'),
            service_type_name=requirement_data.get('service_type_name'),
            preferred_time=requirement_data.get('preferred_time'),
            budget=requirement_data.get('budget'),
            description=requirement_data.get('description'),
            status=0,
            create_time=datetime.now(),
            modify_time=datetime.now()
        )

        self.db.add(new_req)
        self.db.commit()

        return {'success': True, 'id': new_req.id}

    def apply_for_requirement(self, application_data: dict) -> dict:
        """Apply for a customer requirement"""
        existing = self.db.query(CleanerApplicationModel).filter(
            CleanerApplicationModel.requirement_id == application_data.requirement_id,
            CleanerApplicationModel.cleaner_id == application_data.cleaner_id,
            CleanerApplicationModel.is_deleted == 0
        ).first()

        if existing:
            return {'success': False, 'message': 'Already applied'}

        new_app = CleanerApplicationModel(
            requirement_id=application_data.requirement_id,
            cleaner_id=application_data.cleaner_id,
            cleaner_name=application_data.cleaner_name,
            offered_price=application_data.offered_price,
            message=application_data.message,
            status=0,
            create_time=datetime.now(),
            modify_time=datetime.now()
        )

        self.db.add(new_app)
        self.db.commit()

        return {'success': True, 'id': new_app.id}

    def get_applications(self, requirement_id: int) -> List[dict]:
        """Get applications for a requirement"""
        applications = self.db.query(CleanerApplicationModel).filter(
            CleanerApplicationModel.requirement_id == requirement_id,
            CleanerApplicationModel.is_deleted == 0
        ).order_by(CleanerApplicationModel.create_time.desc()).all()

        result = []
        for app in applications:
            result.append({
                'id': app.id,
                'requirement_id': app.requirement_id,
                'cleaner_id': app.cleaner_id,
                'cleaner_name': app.cleaner_name,
                'offered_price': app.offered_price,
                'message': app.message,
                'status': app.status,
                'star_level': None,
                'total_orders': None,
                'total_rating': None,
                'create_time': app.create_time.strftime('%Y-%m-%d %H:%M') if app.create_time else ''
            })

        return result

    def get_admin_requirements(self, status: Optional[int] = None, limit: int = 20, offset: int = 0,
                             guest_name: str = None, guest_phone: str = None,
                             property_type: str = None, service_type: str = None,
                             start_date: str = None, end_date: str = None) -> dict:
        """Get all requirements for admin with pagination and filters"""
        query = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.is_deleted == 0
        )

        if status is not None:
            query = query.filter(CustomerRequirementModel.status == status)

        if guest_name:
            query = query.filter(CustomerRequirementModel.guest_name.like(f'%{guest_name}%'))

        if guest_phone:
            query = query.filter(CustomerRequirementModel.guest_phone.like(f'%{guest_phone}%'))

        if property_type:
            query = query.filter(CustomerRequirementModel.property_type == property_type)

        if service_type:
            query = query.filter(CustomerRequirementModel.service_type_name.like(f'%{service_type}%'))

        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(CustomerRequirementModel.create_time >= start)
            except (ValueError, TypeError):
                pass

        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d')
                end = end.replace(hour=23, minute=59, second=59)
                query = query.filter(CustomerRequirementModel.create_time <= end)
            except (ValueError, TypeError):
                pass

        total = query.count()

        requirements = query.order_by(
            CustomerRequirementModel.create_time.desc()
        ).offset(offset).limit(limit).all()

        result = []
        for req in requirements:
            apps_count = self.db.query(CleanerApplicationModel).filter(
                CleanerApplicationModel.requirement_id == req.id,
                CleanerApplicationModel.is_deleted == 0
            ).count()

            accepted_app = self.db.query(CleanerApplicationModel).filter(
                CleanerApplicationModel.requirement_id == req.id,
                CleanerApplicationModel.status == 1,
                CleanerApplicationModel.is_deleted == 0
            ).first()

            result.append({
                'id': req.id,
                'user_id': req.user_id,
                'guest_name': req.guest_name,
                'guest_phone': req.guest_phone,
                'guest_email': req.guest_email,
                'property_type': req.property_type,
                'bedroom': req.bedroom,
                'bathroom': req.bathroom,
                'living_room': req.living_room,
                'kitchen': req.kitchen,
                'lawn': req.lawn,
                'car_space': req.car_space,
                'square_footage': req.square_footage,
                'service_type_name': req.service_type_name,
                'preferred_time': req.preferred_time,
                'budget': req.budget,
                'description': req.description,
                'status': req.status,
                'assigned_cleaner_id': req.assigned_cleaner_id,
                'create_time': req.create_time.strftime('%Y-%m-%d %H:%M') if req.create_time else '',
                'applications_count': apps_count,
                'accepted_cleaner_id': accepted_app.cleaner_id if accepted_app else None,
                'accepted_cleaner_name': accepted_app.cleaner_name if accepted_app else None
            })

        return {
            'items': result,
            'total': total,
            'page': offset // limit + 1,
            'page_size': limit
        }

    def get_admin_cleaners(self) -> List[dict]:
        """Get all cleaners with workload for admin"""
        cleaners = self.db.query(UserModel).filter(
            UserModel.role.in_(['staff', 'cleaner', 'employee']),
            UserModel.is_deleted == 0,
            UserModel.status == 1
        ).all()

        result = []
        for c in cleaners:
            pending = self.db.query(ServiceOrderModel).filter(
                ServiceOrderModel.assigned_staff_id == c.id,
                ServiceOrderModel.is_deleted == 0,
                ServiceOrderModel.status.in_([1, 2, 3])
            ).count()

            completed = self.db.query(ServiceOrderModel).filter(
                ServiceOrderModel.assigned_staff_id == c.id,
                ServiceOrderModel.is_deleted == 0,
                ServiceOrderModel.status == 4
            ).count()

            result.append({
                'id': c.id,
                'username': c.username,
                'full_name': c.full_name or c.username,
                'star_level': c.star_level or 1,
                'total_orders': c.total_orders or 0,
                'total_rating': c.total_rating or 5.0,
                'pending_tasks': pending,
                'completed_tasks': completed
            })

        return result

    def assign_requirement_to_cleaner(self, requirement_id: int, cleaner_id: int) -> dict:
        """Assign a requirement to a specific cleaner"""
        requirement = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.id == requirement_id
        ).first()

        if not requirement:
            return {'success': False, 'message': 'Requirement not found'}

        cleaner = self.db.query(UserModel).filter(UserModel.id == cleaner_id).first()
        if not cleaner:
            return {'success': False, 'message': 'Cleaner not found'}

        applications = self.db.query(CleanerApplicationModel).filter(
            CleanerApplicationModel.requirement_id == requirement_id,
            CleanerApplicationModel.is_deleted == 0
        ).all()

        for app in applications:
            if app.cleaner_id == cleaner_id:
                app.status = 1
            else:
                app.status = 2

        requirement.status = 1
        requirement.assigned_cleaner_id = cleaner_id
        self.db.commit()

        return {'success': True, 'message': f'Requirement assigned to {cleaner.full_name}'}

    def delete_requirement(self, requirement_id: int) -> dict:
        """Hard delete a requirement"""
        requirement = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.id == requirement_id
        ).first()

        if not requirement:
            return {'success': False, 'message': 'Requirement not found'}

        self.db.delete(requirement)
        self.db.commit()

        return {'success': True, 'message': 'Requirement deleted'}

    def hide_requirement(self, requirement_id: int) -> dict:
        """Soft delete/hide a requirement"""
        requirement = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.id == requirement_id
        ).first()

        if not requirement:
            return {'success': False, 'message': 'Requirement not found'}

        requirement.is_deleted = 1
        self.db.commit()

        return {'success': True, 'message': 'Requirement hidden'}

    def get_all_cleaner_tasks(self, status: Optional[int] = None, limit: int = 20, offset: int = 0,
                             order_no: str = None, cleaner_name: str = None,
                             start_date: str = None, end_date: str = None) -> dict:
        """Get all cleaner tasks for admin with pagination and filters"""
        query = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.is_deleted == 0,
            ServiceOrderModel.assigned_staff_id.isnot(None)
        )

        if status is not None:
            query = query.filter(ServiceOrderModel.status == status)

        if order_no:
            query = query.filter(ServiceOrderModel.order_no.like(f'%{order_no}%'))

        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(ServiceOrderModel.create_time >= start)
            except (ValueError, TypeError):
                pass

        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d')
                end = end.replace(hour=23, minute=59, second=59)
                query = query.filter(ServiceOrderModel.create_time <= end)
            except (ValueError, TypeError):
                pass

        if cleaner_name:
            cleaner_ids = self.db.query(UserModel.id).filter(
                UserModel.full_name.like(f'%{cleaner_name}%')
            ).all()
            cleaner_id_list = [c.id for c in cleaner_ids]
            if cleaner_id_list:
                query = query.filter(ServiceOrderModel.assigned_staff_id.in_(cleaner_id_list))
            else:
                return {'items': [], 'total': 0, 'page': 1, 'page_size': limit}

        total = query.count()

        orders = query.order_by(ServiceOrderModel.create_time.desc()).offset(offset).limit(limit).all()

        result = []
        for order in orders:
            cleaner = self.db.query(UserModel).filter(UserModel.id == order.assigned_staff_id).first()
            service_type = self.db.query(ServiceTypeModel).filter(ServiceTypeModel.type_id == order.service_type_id).first()
            guest = self.db.query(UserModel).filter(UserModel.id == order.guest_id).first()
            requirement = self.db.query(CustomerRequirementModel).filter(
                CustomerRequirementModel.user_id == order.guest_id,
                CustomerRequirementModel.is_deleted == 0
            ).order_by(CustomerRequirementModel.create_time.desc()).first()

            result.append({
                'id': order.order_id,
                'order_no': order.order_no,
                'cleaner_id': order.assigned_staff_id,
                'cleaner_name': cleaner.full_name if cleaner else '',
                'service_type': service_type.type_name if service_type else '',
                'guest_name': guest.full_name if guest else '',
                'guest_phone': guest.phone if guest else '',
                'guest_email': guest.email if guest else '',
                'property_type': requirement.property_type if requirement else '',
                'address': requirement.description if requirement else '',
                'bedroom': requirement.bedroom if requirement else '',
                'bathroom': requirement.bathroom if requirement else '',
                'living_room': requirement.living_room if requirement else '',
                'kitchen': requirement.kitchen if requirement else '',
                'lawn': requirement.lawn if requirement else '',
                'car_space': requirement.car_space if requirement else '',
                'square_footage': requirement.square_footage if requirement else '',
                'preferred_time': requirement.preferred_time if requirement else '',
                'budget': requirement.budget if requirement else '',
                'description': requirement.description if requirement else '',
                'remarks': order.remarks if order.remarks else '',
                'guest_feedback': order.guest_feedback if order.guest_feedback else '',
                'rating': order.rating if order.rating else '',
                'status': order.status,
                'status_text': self._get_status_text(order.status),
                'create_time': order.create_time.strftime('%Y-%m-%d %H:%M') if order.create_time else '',
                'complete_time': order.actual_complete.strftime('%Y-%m-%d %H:%M') if order.actual_complete else ''
            })

        return {
            'items': result,
            'total': total,
            'page': offset // limit + 1,
            'page_size': limit
        }

    def _get_status_text(self, status: int) -> str:
        status_map = {
            0: 'Pending',
            1: 'Assigned',
            2: 'In Progress',
            3: 'Pending Review',
            4: 'Completed',
            5: 'Cancelled'
        }
        return status_map.get(status, 'Unknown')

    def get_cleaner_tasks(self, cleaner_id: int, status: Optional[int] = None, limit: int = 20, offset: int = 0) -> dict:
        """Get tasks for a specific cleaner with pagination"""
        query = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.assigned_staff_id == cleaner_id,
            ServiceOrderModel.is_deleted == 0
        )

        if status is not None:
            query = query.filter(ServiceOrderModel.status == status)

        total = query.count()

        orders = query.order_by(ServiceOrderModel.create_time.desc()).offset(offset).limit(limit).all()

        result = []
        for order in orders:
            service_type = self.db.query(ServiceTypeModel).filter(ServiceTypeModel.type_id == order.service_type_id).first()
            guest = self.db.query(UserModel).filter(UserModel.id == order.guest_id).first()
            requirement = self.db.query(CustomerRequirementModel).filter(
                CustomerRequirementModel.user_id == order.guest_id,
                CustomerRequirementModel.is_deleted == 0
            ).order_by(CustomerRequirementModel.create_time.desc()).first()

            result.append({
                'id': order.order_id,
                'order_no': order.order_no,
                'service_type': service_type.type_name if service_type else '',
                'guest_name': guest.full_name if guest else '',
                'guest_phone': guest.phone if guest else '',
                'property_type': requirement.property_type if requirement else '',
                'address': requirement.description if requirement else '',
                'bedroom': requirement.bedroom if requirement else 0,
                'bathroom': requirement.bathroom if requirement else 0,
                'budget': requirement.budget if requirement else 0,
                'status': order.status,
                'status_text': self._get_status_text(order.status),
                'create_time': order.create_time.strftime('%Y-%m-%d %H:%M') if order.create_time else '',
                'complete_time': order.actual_complete.strftime('%Y-%m-%d %H:%M') if order.actual_complete else ''
            })

        return {
            'items': result,
            'total': total,
            'page': offset // limit + 1,
            'page_size': limit
        }

    def get_customer_requirements(self, user_id: int, limit: int = 20, offset: int = 0) -> dict:
        """Get all requirements for a customer with pagination"""
        query = self.db.query(CustomerRequirementModel).filter(
            CustomerRequirementModel.user_id == user_id,
            CustomerRequirementModel.is_deleted == 0
        )

        total = query.count()

        requirements = query.order_by(CustomerRequirementModel.create_time.desc()).offset(offset).limit(limit).all()

        result = []
        for req in requirements:
            applications = self.db.query(CleanerApplicationModel).filter(
                CleanerApplicationModel.requirement_id == req.id,
                CleanerApplicationModel.is_deleted == 0
            ).all()

            apps_list = []
            for app in applications:
                cleaner = self.db.query(UserModel).filter(UserModel.id == app.cleaner_id).first()
                apps_list.append({
                    'id': app.id,
                    'cleaner_id': app.cleaner_id,
                    'cleaner_name': app.cleaner_name,
                    'cleaner_avatar': cleaner.avatar if cleaner else None,
                    'offered_price': app.offered_price,
                    'status': app.status,
                    'status_text': 'Accepted' if app.status == 1 else ('Rejected' if app.status == 2 else 'Pending'),
                    'create_time': app.create_time.strftime('%Y-%m-%d %H:%M') if app.create_time else ''
                })

            result.append({
                'id': req.id,
                'guest_name': req.guest_name,
                'guest_phone': req.guest_phone,
                'property_type': req.property_type,
                'bedroom': req.bedroom,
                'bathroom': req.bathroom,
                'service_type_name': req.service_type_name,
                'preferred_time': req.preferred_time,
                'budget': req.budget,
                'description': req.description,
                'status': req.status,
                'status_text': self._get_status_text(req.status),
                'assigned_cleaner_id': req.assigned_cleaner_id,
                'create_time': req.create_time.strftime('%Y-%m-%d %H:%M') if req.create_time else '',
                'applications': apps_list
            })

        return {
            'items': result,
            'total': total,
            'page': offset // limit + 1,
            'page_size': limit
        }

    def get_customer_bookings(self, user_id: int, limit: int = 20, offset: int = 0) -> dict:
        """Get all bookings/orders for a customer with pagination"""
        query = self.db.query(ServiceOrderModel).filter(
            ServiceOrderModel.guest_id == user_id,
            ServiceOrderModel.is_deleted == 0
        )

        total = query.count()

        orders = query.order_by(ServiceOrderModel.create_time.desc()).offset(offset).limit(limit).all()

        result = []
        for order in orders:
            cleaner = self.db.query(UserModel).filter(UserModel.id == order.assigned_staff_id).first()
            service_type = self.db.query(ServiceTypeModel).filter(ServiceTypeModel.type_id == order.service_type_id).first()
            requirement = self.db.query(CustomerRequirementModel).filter(
                CustomerRequirementModel.user_id == order.guest_id,
                CustomerRequirementModel.is_deleted == 0
            ).order_by(CustomerRequirementModel.create_time.desc()).first()

            result.append({
                'id': order.order_id,
                'order_no': order.order_no,
                'service_type': service_type.type_name if service_type else '',
                'property_type': requirement.property_type if requirement else '',
                'status': order.status,
                'status_text': self._get_status_text(order.status),
                'assigned_staff': cleaner.full_name if cleaner else '',
                'create_time': order.create_time.strftime('%Y-%m-%d %H:%M') if order.create_time else '',
                'complete_time': order.actual_complete.strftime('%Y-%m-%d %H:%M') if order.actual_complete else ''
            })

        return {
            'items': result,
            'total': total,
            'page': offset // limit + 1,
            'page_size': limit
        }
