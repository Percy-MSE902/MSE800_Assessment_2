from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Numeric, event,Date,Time
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from models.Base import Base

from sqlalchemy.orm import mapped_column

class RoleModel(Base):
    __tablename__ = 'role'

    id = mapped_column(Integer, primary_key=True)
    role_name = mapped_column(String, nullable=True)
    create_time = mapped_column(DateTime, nullable=True)
    modify_time = mapped_column(DateTime, nullable=True)
    is_deleted = mapped_column(Integer, nullable=True)
