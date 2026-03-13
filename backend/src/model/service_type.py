from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from model.Base import Base




class ServiceTypeModel(Base):
    __tablename__ = 'service_type'

    type_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    standard_time: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
