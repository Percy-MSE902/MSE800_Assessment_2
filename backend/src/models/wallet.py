from sqlalchemy import Column, String, Integer, Float, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from models.Base import Base


class WalletModel(Base):
    __tablename__ = 'wallet'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    balance: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    frozen_balance: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class TransactionModel(Base):
    __tablename__ = 'transaction'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, nullable=True, comment='Order ID')
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='pending')
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
