from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Any
from pydantic import BaseModel, field_validator, ConfigDict
from decimal import Decimal
from datetime import datetime

from database import get_db
from models.user import UserModel
from models.wallet import WalletModel, TransactionModel
from core.dependencies import get_current_user, require_permission


router = APIRouter(prefix='/api/wallet', tags=['wallet'])


class WalletSchema(BaseModel):
    id: Optional[int] = None
    user_id: int
    balance: float
    frozen_balance: float

    class Config:
        from_attributes = True


class TransactionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    order_id: Optional[int] = None
    user_id: int
    type: str
    amount: Optional[float] = None
    status: str
    description: Optional[str] = None
    create_time: Optional[str] = None
    
    @field_validator('amount', mode='before')
    @classmethod
    def convert_amount(cls, v: Any) -> Optional[float]:
        if v is None:
            return None
        if isinstance(v, Decimal):
            return float(v)
        return v
    
    @field_validator('create_time', mode='before')
    @classmethod
    def convert_create_time(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat()
        return v
    
    @field_validator('amount', mode='before')
    @classmethod
    def convert_amount(cls, v: Any) -> Optional[float]:
        if v is None:
            return None
        if isinstance(v, Decimal):
            return float(v)
        return v
    
    @field_validator('create_time', mode='before')
    @classmethod
    def convert_create_time(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat()
        return v


class RechargeSchema(BaseModel):
    amount: float


@router.get('/', response_model=WalletSchema)
def get_wallet(
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    wallet = db.query(WalletModel).filter(WalletModel.user_id == current_user.id).first()
    
    if not wallet:
        wallet = WalletModel(user_id=current_user.id, balance=1000.00, frozen_balance=0)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    
    return wallet


@router.post('/recharge')
def recharge(
    data: RechargeSchema,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Recharge amount must be greater than 0")
    
    wallet = db.query(WalletModel).filter(WalletModel.user_id == current_user.id).first()
    if wallet:
        wallet.balance += data.amount
    else:
        wallet = WalletModel(user_id=current_user.id, balance=data.amount, frozen_balance=0)
        db.add(wallet)
    
    transaction = TransactionModel(
        user_id=current_user.id,
        type='recharge',
        amount=data.amount,
        status='completed',
        description='User recharge'
    )
    db.add(transaction)
    db.commit()
    
    return {'message': 'Recharge successful', 'amount': data.amount}


@router.get('/transactions', response_model=List[TransactionSchema])
def get_transactions(
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    transactions = db.query(TransactionModel).filter(
        TransactionModel.user_id == current_user.id
    ).order_by(TransactionModel.create_time.desc()).limit(20).all()
    return transactions


@router.post('/pay/{order_id}')
def pay_order(
    order_id: int,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    from models.service_order import ServiceOrderModel
    
    order = db.query(ServiceOrderModel).filter(ServiceOrderModel.order_id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.guest_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only pay for your own orders")
    
    if order.status != 4:
        raise HTTPException(status_code=400, detail="Order not completed, cannot pay")
    
    existing_payment = db.query(TransactionModel).filter(
        TransactionModel.order_id == order_id,
        TransactionModel.type == 'payment',
        TransactionModel.status == 'completed'
    ).first()
    
    if existing_payment:
        raise HTTPException(status_code=400, detail="Order already paid")
    
    from models.service_type import ServiceTypeModel
    service_type = db.query(ServiceTypeModel).filter(ServiceTypeModel.type_id == order.service_type_id).first()
    
    if not service_type:
        raise HTTPException(status_code=400, detail="Service type not found")
    
    price = Decimal(str(service_type.price))
    
    wallet = db.query(WalletModel).filter(WalletModel.user_id == current_user.id).first()
    
    if not wallet or wallet.balance < price:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    wallet.balance -= price
    
    transaction = TransactionModel(
        order_id=order_id,
        user_id=current_user.id,
        type='payment',
        amount=price,
        status='completed',
        description='Order payment'
    )
    db.add(transaction)
    
    if order.assigned_staff_id:
        cleaner_rate = 0.8
        cleaner_amount = Decimal(str(float(price) * cleaner_rate))
        
        cleaner_wallet = db.query(WalletModel).filter(WalletModel.user_id == order.assigned_staff_id).first()
        if cleaner_wallet:
            cleaner_wallet.balance += cleaner_amount
        else:
            cleaner_wallet = WalletModel(
                user_id=order.assigned_staff_id,
                balance=cleaner_amount
            )
            db.add(cleaner_wallet)
        
        cleaner_transaction = TransactionModel(
            order_id=order_id,
            user_id=order.assigned_staff_id,
            type='earning',
            amount=cleaner_amount,
            status='completed',
            description=f'Earning from order #{order_id}'
        )
        db.add(cleaner_transaction)
    
    db.commit()
    
    # Send notifications
    from models.notification import NotificationModel
    from models.service_order import ServiceOrderModel
    from models.user import UserModel
    
    # Get cleaner user info
    cleaner = db.query(UserModel).filter(UserModel.id == order.assigned_staff_id).first()
    
    # Notification to customer
    customer_notif = NotificationModel(
        user_id=current_user.id,
        title=f'Payment Received for Order #{order.order_no}',
        content=f'Your payment of ${float(price)} for order #{order.order_no} has been processed successfully.',
        type='payment',
        is_read=0
    )
    db.add(customer_notif)
    
    # Notification to cleaner
    if cleaner:
        cleaner_notif = NotificationModel(
            user_id=order.assigned_staff_id,
            title=f'Payment Received for Order #{order.order_no}',
            content=f'Payment of ${float(price)} has been received for order #{order.order_no}. Your earning will be processed after completion.',
            type='payment',
            is_read=0
        )
        db.add(cleaner_notif)
    
    db.commit()


@router.post('/settle/{order_id}')
def settle_to_cleaner(
    order_id: int,
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can settle payments to cleaners")
    
    from models.service_order import ServiceOrderModel
    from models.service_type import ServiceTypeModel
    
    order = db.query(ServiceOrderModel).filter(ServiceOrderModel.order_id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != 4:
        raise HTTPException(status_code=400, detail="Order not completed, cannot settle")
    
    if not order.assigned_staff_id:
        raise HTTPException(status_code=400, detail="No cleaner assigned to this order")
    
    service_type = db.query(ServiceTypeModel).filter(ServiceTypeModel.type_id == order.service_type_id).first()
    
    if not service_type:
        raise HTTPException(status_code=400, detail="Service type not found")
    
    price = float(service_type.price)
    cleaner_rate = 0.8
    cleaner_amount = price * cleaner_rate
    
    cleaner_wallet = db.query(WalletModel).filter(WalletModel.user_id == order.assigned_staff_id).first()
    if cleaner_wallet:
        cleaner_wallet.balance += cleaner_amount
    else:
        cleaner_wallet = WalletModel(user_id=order.assigned_staff_id, balance=cleaner_amount, frozen_balance=0)
        db.add(cleaner_wallet)
    
    transaction = TransactionModel(
        order_id=order_id,
        user_id=order.assigned_staff_id,
        type='settlement',
        amount=cleaner_amount,
        status='completed',
        description=f'Settlement for order {order.order_no}'
    )
    db.add(transaction)
    db.commit()
    
    return {'message': 'Settlement successful', 'amount': cleaner_amount, 'cleaner_id': order.assigned_staff_id}


@router.get('/cleaner-earnings')
def get_cleaner_earnings(
    current_user: UserModel = Depends(require_permission()),
    db: Session = Depends(get_db)
):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can view cleaner earnings")
    
    from models.service_order import ServiceOrderModel
    
    results = db.query(
        UserModel.id,
        UserModel.full_name,
        UserModel.username
    ).filter(UserModel.role == 'cleaner').all()
    
    earnings = []
    for user_id, full_name, username in results:
        total = db.query(TransactionModel).filter(
            TransactionModel.user_id == user_id,
            TransactionModel.type == 'settlement',
            TransactionModel.status == 'completed'
        ).all()
        total_amount = sum(t.amount for t in total)
        
        completed_orders = db.query(ServiceOrderModel).filter(
            ServiceOrderModel.assigned_staff_id == user_id,
            ServiceOrderModel.status == 4
        ).count()
        
        earnings.append({
            'cleaner_id': user_id,
            'cleaner_name': full_name,
            'username': username,
            'completed_orders': completed_orders,
            'total_earnings': total_amount
        })
    
    return earnings
