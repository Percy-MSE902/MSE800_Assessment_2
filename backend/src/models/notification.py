from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from models.Base import Base


class NotificationModel(Base):
    __tablename__ = 'notification'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default='info')
    link_url: Mapped[str] = mapped_column(String(255), nullable=True)
    is_read: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    create_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
