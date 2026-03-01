import sys
sys.path.insert(0, '/Users/liqingchao/workspace/assessment2/backend/src')

from database import SessionLocal
from models.room import RoomModel
import random
from datetime import datetime, timezone
import base64

db = SessionLocal()

print("Clearing existing rooms...")
db.query(RoomModel).delete()
db.commit()
print("Existing rooms cleared.")

room_types = ['Single', 'Double', 'Suite', 'Deluxe Suite']
statuses = [0, 1, 2, 3, 4]

def generate_room_image_url(room_type: str, room_num: int) -> str:
    colors = {
        'Single': '4A90E2',
        'Double': '50C878',
        'Suite': 'F5A623',
        'Deluxe Suite': '9013FE'
    }
    color = colors.get(room_type, 'CCCCCC')
    return f"https://via.placeholder.com/400x300/{color}/FFFFFF?text=Room+{room_num}"

def generate_floor_plan_url(room_type: str, room_num: int) -> str:
    plans = {
        'Single': 'https://via.placeholder.com/600x400/E0E0E0/333333?text=Single+Room+Layout',
        'Double': 'https://via.placeholder.com/600x400/E0E0E0/333333?text=Double+Room+Layout',
        'Suite': 'https://via.placeholder.com/600x400/E0E0E0/333333?text=Suite+Layout',
        'Deluxe Suite': 'https://via.placeholder.com/600x400/E0E0E0/333333?text=Deluxe+Suite+Layout'
    }
    return plans.get(room_type, 'https://via.placeholder.com/600x400/E0E0E0/333333?text=Floor+Plan')

rooms = []
floor = 1
room_num = 1

print("Creating 5000 rooms with images...")

for i in range(5000):
    if room_num > 20:
        floor += 1
        room_num = 1
    
    rt = random.choice(room_types)
    room_number_str = f"{floor}{str(room_num).zfill(3)}"
    
    room = RoomModel(
        room_number=room_number_str,
        floor=floor,
        room_type=rt,
        capacity=random.randint(1, 4),
        price=round(random.uniform(100, 1000), 2),
        status=random.choice(statuses),
        image_url=generate_room_image_url(rt, room_num),
        floor_plan_url=generate_floor_plan_url(rt, room_num),
        description=f'Room {room_number_str} - {rt}',
        create_time=datetime.now(timezone.utc),
        modify_time=datetime.now(timezone.utc),
        is_deleted=0
    )
    rooms.append(room)
    room_num += 1
    
    if (i + 1) % 500 == 0:
        db.bulk_save_objects(rooms)
        db.commit()
        print(f"Inserted {i + 1} rooms with images...")
        rooms = []

if rooms:
    db.bulk_save_objects(rooms)
    db.commit()

print("Done! 5000 rooms with images inserted successfully.")
db.close()
