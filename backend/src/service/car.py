from fastapi import Depends
from sqlalchemy.orm import Session

from service.ServiceBase import ServiceBase
from model.car import CarModel
from cruds.car import car_crud
from schemas.car import CarSchema, CarCreateSchema, CarUpdateSchema


# --------------------------------------------------
# Service Layer
# --------------------------------------------------
# This service layer handles business logic for the model.
# It wraps the CRUD layer and can be extended with
# custom validation, permission checks, or other
# domain-specific logic.

class car(ServiceBase[CarModel, CarCreateSchema, CarUpdateSchema]):
    """
    Car service class.

    Inherits from ServiceBase to reuse generic CRUD
    operations such as create, read, update, delete,
    and pagination.

    Override methods here to implement custom
    business logic for this model.
    """
    def __init__(self, db: Session):
        crud_instance = super().get_crud(crud_cls=car_crud, model_cls=CarModel)
        super().__init__(crud=crud_instance, db=db)
