# init_db.py - Simple SQLite initialization
import os as _os
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker
from database import DatabaseFactory, DATABASES
from datetime import datetime

BASE_DIR = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), '..'))

def create_tables_sqlite():
    db_path = _os.path.join(BASE_DIR, "housekeeping.db")
    print(f"DB path: {db_path}")
    
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    metadata = MetaData()

    # User table
    user_table = Table('user', metadata,
        Column('id', Integer, primary_key=True),
        Column('username', String(50), unique=True, nullable=False),
        Column('password', String(255), nullable=False),
        Column('full_name', String(100), nullable=False),
        Column('email', String(100)),
        Column('phone', String(20)),
        Column('role', String(20), default='guest'),
        Column('status', Integer, default=1),
        Column('create_time', DateTime, default=datetime.utcnow),
        Column('modify_time', DateTime, default=datetime.utcnow),
        Column('is_deleted', Integer, default=0)
    )

    # Room table
    room_table = Table('room', metadata,
        Column('room_id', Integer, primary_key=True),
        Column('room_number', String(20), unique=True, nullable=False),
        Column('floor', Integer, nullable=False),
        Column('room_type', String(30), nullable=False),
        Column('capacity', Integer, default=2),
        Column('price', Float, nullable=False),
        Column('status', Integer, default=0),
        Column('last_clean_time', DateTime),
        Column('description', String(500)),
        Column('create_time', DateTime, default=datetime.utcnow),
        Column('modify_time', DateTime, default=datetime.utcnow),
        Column('is_deleted', Integer, default=0)
    )

    # Service type table
    service_type_table = Table('service_type', metadata,
        Column('type_id', Integer, primary_key=True),
        Column('type_name', String(50), nullable=False),
        Column('description', String(200)),
        Column('standard_time', Integer, default=30),
        Column('price', Float, default=0),
        Column('is_active', Integer, default=1),
        Column('create_time', DateTime, default=datetime.utcnow),
        Column('modify_time', DateTime, default=datetime.utcnow),
        Column('is_deleted', Integer, default=0)
    )

    # Service order table
    service_order_table = Table('service_order', metadata,
        Column('order_id', Integer, primary_key=True),
        Column('order_no', String(30), unique=True, nullable=False),
        Column('room_id', Integer, nullable=False),
        Column('guest_id', Integer, nullable=False),
        Column('service_type_id', Integer, nullable=False),
        Column('assigned_staff_id', Integer),
        Column('status', Integer, default=0),
        Column('priority', Integer, default=0),
        Column('request_time', DateTime, nullable=False),
        Column('scheduled_start', DateTime),
        Column('scheduled_end', DateTime),
        Column('actual_start', DateTime),
        Column('actual_complete', DateTime),
        Column('remarks', String(500)),
        Column('guest_feedback', String(500)),
        Column('rating', Integer),
        Column('create_time', DateTime, default=datetime.utcnow),
        Column('modify_time', DateTime, default=datetime.utcnow),
        Column('is_deleted', Integer, default=0)
    )

    # Inventory item table
    inventory_item_table = Table('inventory_item', metadata,
        Column('item_id', Integer, primary_key=True),
        Column('item_name', String(50), nullable=False),
        Column('category', String(30), nullable=False),
        Column('quantity', Integer, default=0),
        Column('min_stock', Integer, default=10),
        Column('unit', String(10), nullable=False),
        Column('location', String(50)),
        Column('is_active', Integer, default=1),
        Column('create_time', DateTime, default=datetime.utcnow),
        Column('modify_time', DateTime, default=datetime.utcnow),
        Column('is_deleted', Integer, default=0)
    )

    # Resource table
    resource_table = Table('resource', metadata,
        Column('id', Integer, primary_key=True),
        Column('resource_name', String(100)),
        Column('resource_link', String(255)),
        Column('resource_method', String(10))
    )

    # Role table
    role_table = Table('role', metadata,
        Column('id', Integer, primary_key=True),
        Column('role_name', String(50), unique=True, nullable=False)
    )

    # User role table
    user_role_table = Table('user_role', metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', Integer, nullable=False),
        Column('role_id', Integer, nullable=False)
    )

    # Role resource table
    role_resource_table = Table('role_resource', metadata,
        Column('id', Integer, primary_key=True),
        Column('role_id', Integer, nullable=False),
        Column('resource_id', Integer, nullable=False)
    )

    metadata.create_all(engine)
    print("Tables created!")
    
    # Insert initial data
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Insert test users (password: admin123)
    session.execute(text("""
        INSERT INTO user (username, password, full_name, email, phone, role, status)
        VALUES ('admin', 'admin123', 'System Admin', 'admin@hotel.com', '13800000000', 'admin', 1),
               ('cleaner1', 'admin123', 'Cleaner Zhang San', 'cleaner1@hotel.com', '13900000001', 'cleaner', 1),
               ('cleaner2', 'admin123', 'Cleaner Li Si', 'cleaner2@hotel.com', '13900000002', 'cleaner', 1),
               ('guest1', 'admin123', 'Zhang San', 'zhangsan@email.com', '13800000001', 'guest', 1)
    """))
    
    # Insert rooms
    session.execute(text("""
        INSERT INTO room (room_number, floor, room_type, capacity, price, status)
        VALUES ('1001', 1, 'Single Room', 1, 199.00, 0),
               ('1002', 1, 'Double Room', 2, 299.00, 1),
               ('1003', 1, 'Single Room', 1, 199.00, 2),
               ('1004', 1, 'Suite', 3, 599.00, 3),
               ('2001', 2, 'Double Room', 2, 299.00, 0),
               ('2002', 2, 'Double Room', 2, 299.00, 1),
               ('2003', 2, 'Suite', 3, 599.00, 0),
               ('3001', 3, 'Deluxe Suite', 4, 999.00, 0)
    """))
    
    # Insert service types
    session.execute(text("""
        INSERT INTO service_type (type_name, description, standard_time, price)
        VALUES ('Regular Cleaning', 'Standard room cleaning service', 30, 50.00),
               ('Deep Cleaning', 'Comprehensive deep cleaning', 60, 100.00),
               ('Bed Sheet Change', 'Replace bed sheets and covers', 15, 20.00),
               ('Express Cleaning', 'Priority handling', 20, 80.00)
    """))
    
    # Insert inventory
    session.execute(text("""
        INSERT INTO inventory_item (item_name, category, quantity, min_stock, unit)
        VALUES ('Towel', 'Textile', 150, 50, 'piece'),
               ('Bed Sheet', 'Textile', 80, 30, 'piece'),
               ('Toothbrush', 'Toiletries', 200, 100, 'piece'),
               ('Shampoo', 'Toiletries', 45, 50, 'bottle'),
               ('Tissue Paper', 'Cleaning Supplies', 300, 100, 'box'),
               ('Disinfectant', 'Cleaning Supplies', 25, 20, 'bottle')
    """))
    
    # Insert roles
    session.execute(text("""
        INSERT INTO role (role_name) VALUES ('admin'), ('cleaner'), ('guest')
    """))
    
    # Insert resources (API endpoints)
    session.execute(text("""
        INSERT INTO resource (resource_name, resource_link, resource_method) VALUES
        ('Service Order List', '/api/service-order', 'GET'),
        ('Service Order Create', '/api/service-order', 'POST'),
        ('Service Order Update', '/api/service-order/{order_id}', 'PUT'),
        ('Service Order Delete', '/api/service-order/{order_id}', 'DELETE'),
        ('Assign Staff', '/api/service-order/assign/{order_id}', 'POST'),
        ('Start Work', '/api/service-order/start/{order_id}', 'POST'),
        ('Complete Work', '/api/service-order/complete/{order_id}', 'POST'),
        ('Room List', '/api/room', 'GET'),
        ('Room Create', '/api/room', 'POST'),
        ('Room Update', '/api/room/{room_id}', 'PUT'),
        ('User List', '/api/user', 'GET'),
        ('User Create', '/api/user', 'POST'),
        ('User Update', '/api/user/{user_id}', 'PUT'),
        ('User Delete', '/api/user/{user_id}', 'DELETE'),
        ('Inventory List', '/api/inventory', 'GET'),
        ('Inventory Create', '/api/inventory', 'POST'),
        ('Inventory Update', '/api/inventory/{item_id}', 'PUT'),
        ('Service Type List', '/api/service-type', 'GET'),
        ('Wallet', '/api/wallet', 'GET'),
        ('Wallet Recharge', '/api/wallet/recharge', 'POST')
    """))
    
    # Insert user roles (admin=1, cleaner=2, guest=3 based on insert order)
    session.execute(text("""
        INSERT INTO user_role (user_id, role_id) VALUES 
        (1, 1),  -- admin user -> admin role
        (2, 2),  -- cleaner1 -> cleaner role
        (3, 2),  -- cleaner2 -> cleaner role
        (4, 3)   -- guest1 -> guest role
    """))
    
    # Insert role resources
    # Admin role (role_id=1) gets all resources
    session.execute(text("""
        INSERT INTO role_resource (role_id, resource_id) 
        SELECT 1, id FROM resource
    """))
    
    # Cleaner role (role_id=2) gets limited resources
    session.execute(text("""
        INSERT INTO role_resource (role_id, resource_id) VALUES 
        (2, 1),  -- Service Order List
        (2, 6),  -- Start Work
        (2, 7),  -- Complete Work
        (2, 8),  -- Room List
        (2, 19), -- Wallet
        (2, 20)  -- Wallet Recharge
    """))
    
    # Guest role (role_id=3) gets limited resources
    session.execute(text("""
        INSERT INTO role_resource (role_id, resource_id) VALUES 
        (3, 1),  -- Service Order List
        (3, 2),  -- Service Order Create
        (3, 8),  -- Room List
        (3, 19), -- Wallet
        (3, 20)  -- Wallet Recharge
    """))
    
    session.commit()
    session.close()
    print("SQLite database created successfully with initial data!")

def init_database(db_type: str = "sqlite"):
    if db_type == "sqlite":
        create_tables_sqlite()
    else:
        print(f"Database type {db_type} not supported in this mode")

if __name__ == "__main__":
    init_database("sqlite")
