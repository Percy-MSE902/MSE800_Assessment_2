
import os
import re
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import declarative_base
# Base class for SQLAlchemy models
Base = declarative_base()

DB_HOST = "127.0.0.1"
DB_NAME = "housekeeping"
DB_USER = "root"
DB_PASS = "rootpassword"
# ==================================
# CONFIG — output folders
# ==================================
PROJECT_NAME = "/backend/src"
MODELS_DIR = f"./{PROJECT_NAME}/models"
SCHEMAS_DIR = f"./{PROJECT_NAME}/schemas"
CRUD_DIR = f"./{PROJECT_NAME}/cruds"
API_DIR = f"./{PROJECT_NAME}/apis"
SERVICES_DIR = f"./{PROJECT_NAME}/services"
# ==================================
# SETUP — create SQLAlchemy engine
# ==================================
engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
)
inspector = inspect(engine)
# Create folders if not exist
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(SCHEMAS_DIR, exist_ok=True)
os.makedirs(CRUD_DIR, exist_ok=True)
os.makedirs(API_DIR, exist_ok=True)
os.makedirs(SERVICES_DIR, exist_ok=True)
# ==================================
# TYPE MAPPING — MySQL → SQLAlchemy
# ==================================
def map_sql_to_sqla(sql_type: str):
    s = sql_type.lower()
    if "int" in s:
        return "Integer"
    if "decimal" in s or "float" in s or "double" in s:
        m = re.search(r"\((\d+),(\d+)\)", s)
        if m:
            return f"Numeric({m.group(1)},{m.group(2)})"
        return "Float"
    if "char" in s or "text" in s:
        return "String"
    if "datetime" in s:
        return "DateTime"
    if "date" in s:
        return "Date"
    if "time" in s:
        return "Time"
    if "bool" in s or s.startswith("tinyint(1)"):
        return "Boolean"
    return "String"
# ==================================
# TYPE MAPPING — MySQL → Python types for Pydantic
# ==================================
def map_sql_to_py(sql_type: str):
    s = sql_type.lower()
    if "int" in s:
        return "int", None
    if "decimal" in s or "float" in s or "double" in s:
        return "float", None
    if "char" in s or "text" in s:
        m = re.search(r"\((\d+)\)", s)
        if m:
            return "str", int(m.group(1))
        return "str", None
    if "datetime" in s:
        return "datetime", None
    if "date" in s:
        return "date", None
    if "time" in s:
        return "time", None
    if "bool" in s or s.startswith("tinyint(1)"):
        return "bool", None
    return "str", None
# ==================================
# MAIN LOOP — generate files for each table
# ==================================
tables = inspector.get_table_names()
for table in tables:
    if table!="car":
        continue
    columns = inspector.get_columns(table)
    # Convert table_name → TableName
    class_name = "".join(x.capitalize() for x in table.split("_"))
    model_file = f"{MODELS_DIR}/{table}.py"
    schema_file = f"{SCHEMAS_DIR}/{table}.py"
    crud_file = f"{CRUD_DIR}/{table}.py"
    service_file = f"{SERVICES_DIR}/{table}.py"
    api_file = f"{API_DIR}/{table}.py"
    # ==================================
    # MODEL
    # ==================================
    model_lines = []
    model_class = f"{class_name}Model"
    model_lines.append("from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Numeric, event,Date,Time\n")
    model_lines.append("from sqlalchemy.ext.declarative import declarative_base\n")
    model_lines.append("from datetime import datetime\n\n")
    model_lines.append("from models.Base import Base\n\n")
    model_lines.append("from sqlalchemy.orm import mapped_column\n\n")
    model_lines.append(f"class {model_class}(Base):\n")
    model_lines.append(f"    __tablename__ = '{table}'\n\n")
    # Detect primary keys (works for composite PK)
    pk_list = inspector.get_pk_constraint(table).get("constrained_columns", [])
    # Add all columns
    for col in columns:
        col_name = col["name"]
        col_type = map_sql_to_sqla(str(col["type"]))
        is_pk = col_name in pk_list
        if is_pk:
            model_lines.append(f"    {col_name} = mapped_column({col_type}, primary_key=True)\n")
        else:
            model_lines.append(f"    {col_name} = mapped_column({col_type}, nullable=True)\n")
    # Auto update updateddatetime
    with open(model_file, "w") as f:
        f.write("".join(model_lines))
    # ==================================
    # SCHEMAS
    # ==================================
    schema_lines = []
    schema_class = f"{class_name}Schema"
    create_schema_class = f"{class_name}CreateSchema"
    update_schema_class = f"{class_name}UpdateSchema"
    schema_lines.append("from pydantic import BaseModel,Field, constr\n")
    schema_lines.append("from datetime import datetime, date, time\n")
    schema_lines.append("from typing import Optional\n\n")
    skip_create = {"updateddatetime"}
    skip_update = {"updateddatetime"}
    # GET schema
    schema_lines.append(f"class {schema_class}(BaseModel):\n")
    for col in columns:
        col_name = col["name"]
        py_type, max_length = map_sql_to_py(str(col["type"]))
        field_type = f"str" if py_type == "str" and max_length else py_type
        if py_type == "str" and max_length is not None:
            line = f"    {col_name}: Optional[str] = Field(None, max_length={max_length})"
        else:
            line = f"    {col_name}: Optional[{field_type}] = None"
        schema_lines.append(line+"\n")
    schema_lines.append("\n    class Config:\n")
    schema_lines.append("        from_attributes = True\n")
    schema_lines.append("        json_encoders = {\n")
    schema_lines.append("            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S') if v else None,\n")
    schema_lines.append("            date: lambda v: v.strftime('%Y-%m-%d') if v else None,\n")
    schema_lines.append("            time: lambda v: v.strftime('%H:%M:%S') if v else None,\n")
    schema_lines.append("        }\n\n")
    # POST schema
    schema_lines.append(f"class {create_schema_class}(BaseModel):\n")
    for col in columns:
        col_name = col["name"]
        if col_name in skip_create:
            continue
        py_type, max_length = map_sql_to_py(str(col["type"]))
        is_pk = col_name in pk_list
        field_type = f"str" if py_type == "str" and max_length else py_type
        if is_pk:
            schema_lines.append(f"    {col_name}: {field_type}\n")
        else:
            if py_type == "str" and max_length is not None:
                line = f"    {col_name}: Optional[str] = Field(None, max_length={max_length})"
            else:
                line = f"    {col_name}: Optional[{field_type}] = None"
            schema_lines.append(line+"\n")
    schema_lines.append("\n    class Config:\n")
    schema_lines.append("        from_attributes = True\n\n")
    # PUT schema
    schema_lines.append(f"class {update_schema_class}(BaseModel):\n")
    for col in columns:
        col_name = col["name"]
        if col_name in skip_update or col_name in pk_list:
            continue
        py_type, max_length = map_sql_to_py(str(col["type"]))
        field_type = f"str" if py_type == "str" and max_length else py_type
        if py_type == "str" and max_length is not None:
            line = f"    {col_name}: Optional[str] = Field(None, max_length={max_length})"
        else:
            line = f"    {col_name}: Optional[{field_type}] = None"
    schema_lines.append(line+"\n")
    schema_lines.append("\n    class Config:\n")
    schema_lines.append("        from_attributes = True\n")
    with open(schema_file, "w") as f:
        f.write("".join(schema_lines))
    # ==================================
    # CRUD
    # ==================================
        
    crud_lines = []
    # ----------- Imports -----------
    crud_lines.append("from sqlalchemy.orm import Session\n")
    crud_lines.append("from cruds.CRUDBase import CRUDBase\n")
    crud_lines.append(f"from models.{table} import {model_class}\n")
    crud_lines.append(
        f"from schemas.{table} import {schema_class}, {create_schema_class}, {update_schema_class}\n\n"
    )

    # ----------- CRUD Layer -----------
    crud_lines.append("# --------------------------------------------------\n")
    crud_lines.append("# CRUD Layer\n")
    crud_lines.append("# --------------------------------------------------\n")
    crud_lines.append(
        "# This class provides database-level operations\n"
    )
    crud_lines.append(
        "# for the corresponding model.\n"
    )
    crud_lines.append(
        "# It inherits common CRUD methods from CRUDBase:\n"
    )
    crud_lines.append(
        "# - get\n"
    )
    crud_lines.append(
        "# - get_all\n"
    )
    crud_lines.append(
        "# - create\n"
    )
    crud_lines.append(
        "# - update\n"
    )
    crud_lines.append(
        "# - delete\n"
    )
    crud_lines.append(
        "# - soft_delete\n"
    )
    crud_lines.append(
        "# - get_multi (pagination & filtering)\n\n"
    )

    # ----------- CRUD Class -----------
    crud_lines.append(
        f"class {table}_crud(CRUDBase[{model_class}, {create_schema_class}, {update_schema_class}]):\n"
    )
    crud_lines.append("    \"\"\"\n")
    crud_lines.append(f"    {table.capitalize()} CRUD class.\n\n")
    crud_lines.append(
        "    Extends the generic CRUDBase class to perform\n"
    )
    crud_lines.append(
        "    database operations for the associated model.\n\n"
    )
    crud_lines.append(
        "    Override methods here if model-specific query\n"
    )
    crud_lines.append(
        "    behavior is required.\n"
    )
    crud_lines.append("    \"\"\"\n")
    crud_lines.append("    pass\n\n")

    with open(crud_file, "w") as f:
        f.write("".join(crud_lines))

     # ==================================
    # SERVICE
    # ==================================
    service_lines = []

    # ----------- Imports -----------
    service_lines.append("from fastapi import Depends\n")
    service_lines.append("from sqlalchemy.orm import Session\n")
    service_lines.append("from services.ServiceBase import ServiceBase\n")
    service_lines.append(f"from models.{table} import {model_class}\n")
    service_lines.append(f"from cruds.{table} import {table}_crud\n")
    service_lines.append(
        f"from schemas.{table} import {schema_class}, {create_schema_class}, {update_schema_class}\n\n"
    )

    # ----------- Service Layer -----------
    service_lines.append("# --------------------------------------------------\n")
    service_lines.append("# Service Layer\n")
    service_lines.append("# --------------------------------------------------\n")
    service_lines.append(
        "# This service layer handles business logic for the model.\n"
    )
    service_lines.append(
        "# It wraps the CRUD layer and can be extended with\n"
    )
    service_lines.append(
        "# custom validation, permission checks, or other\n"
    )
    service_lines.append(
        "# domain-specific logic.\n\n"
    )

    # ----------- Service Class -----------
    service_lines.append(
        f"class {table}(ServiceBase[{model_class}, {create_schema_class}, {update_schema_class}]):\n"
    )
    service_lines.append("    \"\"\"\n")
    service_lines.append(f"    {table.capitalize()} service class.\n\n")
    service_lines.append(
        "    Inherits from ServiceBase to reuse generic CRUD\n"
    )
    service_lines.append(
        "    operations such as create, read, update, delete,\n"
    )
    service_lines.append(
        "    and pagination.\n\n"
    )
    service_lines.append(
        "    Override methods here to implement custom\n"
    )
    service_lines.append(
        "    business logic for this model.\n"
    )
    service_lines.append("    \"\"\"\n")
    service_lines.append(
        "    def __init__(self, db: Session):\n"
    )
    service_lines.append(
        f"        crud_instance = super().get_crud(crud_cls={table}_crud, model_cls={model_class})\n"
    )
    service_lines.append(
        "        super().__init__(crud=crud_instance, db=db)\n"
    )

    with open(service_file, "w") as f:
        f.write("".join(service_lines))   
    # ==================================
    # API ROUTER
    # ==================================
    api_lines = []

    # ----------- Imports -----------
    api_lines.append("import math\n")
    api_lines.append("from fastapi import APIRouter, Depends, HTTPException\n")
    api_lines.append("from sqlalchemy.orm import Session\n")
    api_lines.append("from typing import Any, Dict, List, Optional\n\n")

    # ----------- Dependencies -----------
    api_lines.append("# Database session and service dependencies\n")
    api_lines.append("from schemas.PaginationRequest import PaginationRequest\n")
    api_lines.append("from core.dependencies import get_service\n")
    api_lines.append(f"from services.{table} import {table}\n\n")

    # ----------- Pydantic Schemas -----------
    api_lines.append("# Pydantic schemas for request and response validation\n")
    api_lines.append(
        f"from schemas.{table} import {schema_class}, {create_schema_class}, {update_schema_class}\n\n"
    )

    # ----------- Router Definition -----------
    api_lines.append("# Create API router with prefix and tag\n")
    api_lines.append(f"router = APIRouter(prefix='/{table}', tags=['{table}'])\n\n")

    # ----------- Read All -----------
    api_lines.append(
        f"@router.get('/', response_model=List[{schema_class}])\n"
    )
    api_lines.append(
        f"def read_all(service: {table} = Depends(get_service({table}))):\n"
    )
    api_lines.append("    \"\"\"\n    Retrieve all records.\n    \"\"\"\n")
    api_lines.append("    return service.get_all()\n\n")

    # ----------- Read One by PK -----------
    pk_params = ", ".join(pk_list)
    pk_path = "/".join(f"{{{pk}}}" for pk in pk_list)

    api_lines.append(f"@router.get('/{pk_path}', response_model={schema_class})\n")
    api_lines.append(
        f"def read_item({pk_params}, service: {table} = Depends(get_service({table}))):\n"
    )
    api_lines.append("    \"\"\"\n    Retrieve a single record by primary key.\n    \"\"\"\n")
    api_lines.append(f"    db_obj = service.get({pk_params})\n")
    api_lines.append("    if not db_obj:\n")
    api_lines.append("        raise HTTPException(status_code=404, detail='Item not found')\n")
    api_lines.append("    return db_obj\n\n")

    # ----------- Create -----------
    api_lines.append(
        f"@router.post('/', response_model={schema_class})\n"
    )
    api_lines.append(
        f"def create_item(item_in: {create_schema_class}, service: {table} = Depends(get_service({table}))):\n"
    )
    api_lines.append("    \"\"\"\n    Create a new record.\n    \"\"\"\n")
    api_lines.append("    return service.create(item_in)\n\n")

    # ----------- Update -----------
    api_lines.append(
        f"@router.put('/{pk_path}', response_model={schema_class})\n"
    )
    api_lines.append(
        f"def update_item({pk_params}, item_in: {update_schema_class}, service: {table} = Depends(get_service({table}))):\n"
    )
    api_lines.append("    \"\"\"\n    Update an existing record by primary key.\n    \"\"\"\n")
    api_lines.append(f"    db_obj = service.get({pk_params})\n")
    api_lines.append("    if not db_obj:\n")
    api_lines.append("        raise HTTPException(status_code=404, detail='Item not found')\n")
    api_lines.append("    return service.update(db_obj, item_in)\n\n")

    # ----------- Delete -----------
    api_lines.append(f"@router.delete('/{pk_path}')\n")
    api_lines.append(
        f"def delete_item({pk_params}, service: {table} = Depends(get_service({table}))):\n"
    )
    api_lines.append("    \"\"\"\n    Delete a record by primary key.\n    \"\"\"\n")
    api_lines.append(f"    db_obj = service.get({pk_params})\n")
    api_lines.append("    if not db_obj:\n")
    api_lines.append("        raise HTTPException(status_code=404, detail='Item not found')\n")
    api_lines.append("    service.delete(db_obj)\n")
    api_lines.append("    return {'ok': True}\n\n")

    # ----------- Paginated Read -----------
    api_lines.append(f"@router.post('/paginated', response_model=Dict[str, Any])\n")
    api_lines.append(
        f"def read_paginated(pageParam: PaginationRequest, service: {table} = Depends(get_service({table}))):\n"
    )
    api_lines.append("    \"\"\"\n    Paginated list of records with optional filters and sorting.\n    \"\"\"\n")
    api_lines.append("    filter_dict: Dict[str, Any] = {}\n")
    api_lines.append("    if pageParam.filters:\n")
    api_lines.append("        try:\n")
    api_lines.append("            filter_dict = pageParam.filters\n")
    api_lines.append("        except Exception:\n")
    api_lines.append('            raise HTTPException(status_code=400, detail="Invalid filters JSON")\n\n')
    api_lines.append(
        "    total, items = service.get_paginated(\n"
    )
    api_lines.append("        page=pageParam.page,\n")
    api_lines.append("        page_size=pageParam.page_size,\n")
    api_lines.append("        filters=filter_dict,\n")
    api_lines.append("        order_by=pageParam.order_by\n")
    api_lines.append("    )\n")
    api_lines.append("    return {\n")
    api_lines.append("        'current_page': pageParam.page,\n")
    api_lines.append("        'page_total': math.ceil(total / pageParam.page_size),\n")
    api_lines.append("        'total': total,\n")
    api_lines.append(
        f"        'items': [{schema_class}.model_validate(item, from_attributes=True) for item in items]\n"
    )
    api_lines.append("    }\n")
    with open(api_file, "w") as f:
        f.write("".join(api_lines))
print("✔ All model & schema files generated successfully!")