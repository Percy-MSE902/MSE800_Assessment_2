from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from models.Base import Base


class RoomModel(Base):
    __tablename__ = 'room'

    room_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    room_type: Mapped[str] = mapped_column(String(30), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_clean_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    floor_plan_url: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    modify_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
