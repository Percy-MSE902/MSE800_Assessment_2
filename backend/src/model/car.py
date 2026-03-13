from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Numeric, event,Date,Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column

from model.Base import Base




class CarModel(Base):
    __tablename__ = 'car'

    car_id = mapped_column(Integer, primary_key=True)
    make = mapped_column(String, nullable=True)
    model = mapped_column(String, nullable=True)
    year = mapped_column(Integer, nullable=True)
    mileage = mapped_column(Integer, nullable=True)
    is_available = mapped_column(Integer, nullable=True)
    min_days = mapped_column(Integer, nullable=True)
    max_days = mapped_column(Integer, nullable=True)
    license_plate = mapped_column(String, nullable=True)
    color = mapped_column(String, nullable=True)
    daily_rate = mapped_column(Float, nullable=True)
    category_id = mapped_column(Integer, nullable=True)
    location_id = mapped_column(Integer, nullable=True)
    create_time = mapped_column(DateTime, nullable=True)
    modify_time = mapped_column(DateTime, nullable=True)
    is_deleted = mapped_column(Integer, nullable=True)
