# init_db.py - MySQL database initialization
import os as _os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import engine
from datetime import datetime

def init_database():
    """
    Initialize the MySQL database with tables and initial data.
    """
    # Import all models to ensure they are registered with the Base
    from model.user import UserModel
    from model.room import RoomModel
    from model.service_type import ServiceTypeModel
    from model.service_order import ServiceOrderModel
    from model.inventory_item import InventoryItemModel
    from model.resource import ResourceModel
    from model.role import RoleModel
    from model.user_role import UserRoleModel
    from model.role_resource import RoleResourceModel

    # Import Base from database module
    from database import Base

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if initial data already exists
        user_count = db.execute(text("SELECT COUNT(*) FROM user")).scalar()
        if user_count > 0:
            print("Initial data already exists, skipping...")
            return

        # Insert initial data
        # Insert roles
        db.execute(text("""
            INSERT INTO role (role_name) VALUES ('admin'), ('cleaner'), ('guest')
        """))

        # Insert test users (password will be hashed by the application)
        db.execute(text("""
            INSERT INTO user (username, password, full_name, email, phone, role, status)
            VALUES ('admin', 'admin123', 'System Admin', 'admin@hotel.com', '13800000000', 'admin', 1),
                   ('cleaner1', 'admin123', 'Cleaner Zhang San', 'cleaner1@hotel.com', '13900000001', 'cleaner', 1),
                   ('cleaner2', 'admin123', 'Cleaner Li Si', 'cleaner2@hotel.com', '13900000002', 'cleaner', 1),
                   ('guest1', 'admin123', 'Zhang San', 'zhangsan@email.com', '13800000001', 'guest', 1)
        """))

        # Insert user roles
        db.execute(text("""
            INSERT INTO user_role (user_id, role_id) VALUES
            (1, 1),  -- admin user -> admin role
            (2, 2),  -- cleaner1 -> cleaner role
            (3, 2),  -- cleaner2 -> cleaner role
            (4, 3)   -- guest1 -> guest role
        """))

        # Insert rooms
        db.execute(text("""
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
        db.execute(text("""
            INSERT INTO service_type (type_name, description, standard_time, price)
            VALUES ('Regular Cleaning', 'Standard room cleaning service', 30, 50.00),
                   ('Deep Cleaning', 'Comprehensive deep cleaning', 60, 100.00),
                   ('Bed Sheet Change', 'Replace bed sheets and covers', 15, 20.00),
                   ('Express Cleaning', 'Priority handling', 20, 80.00)
        """))

        # Insert inventory
        db.execute(text("""
            INSERT INTO inventory_item (item_name, category, quantity, min_stock, unit)
            VALUES ('Towel', 'Textile', 150, 50, 'piece'),
                   ('Bed Sheet', 'Textile', 80, 30, 'piece'),
                   ('Toothbrush', 'Toiletries', 200, 100, 'piece'),
                   ('Shampoo', 'Toiletries', 45, 50, 'bottle'),
                   ('Tissue Paper', 'Cleaning Supplies', 300, 100, 'box'),
                   ('Disinfectant', 'Cleaning Supplies', 25, 20, 'bottle')
        """))

        # Insert resources (API endpoints)
        db.execute(text("""
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

        # Insert role resources
        # Admin role (role_id=1) gets all resources
        db.execute(text("""
            INSERT INTO role_resource (role_id, resource_id)
            SELECT 1, id FROM resource
        """))

        # Cleaner role (role_id=2) gets limited resources
        db.execute(text("""
            INSERT INTO role_resource (role_id, resource_id) VALUES
            (2, 1),  -- Service Order List
            (2, 6),  -- Start Work
            (2, 7),  -- Complete Work
            (2, 8),  -- Room List
            (2, 19), -- Wallet
            (2, 20)  -- Wallet Recharge
        """))

        # Guest role (role_id=3) gets limited resources
        db.execute(text("""
            INSERT INTO role_resource (role_id, resource_id) VALUES
            (3, 1),  -- Service Order List
            (3, 2),  -- Service Order Create
            (3, 8),  -- Room List
            (3, 19), -- Wallet
            (3, 20)  -- Wallet Recharge
        """))

        db.commit()
        print("MySQL database initialized successfully with initial data!")

    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
