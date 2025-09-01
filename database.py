import motor.motor_asyncio
from models.user import UserModel
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "eko_backend"  # You can change this to your preferred database name

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
database = client[DB_NAME]

# Collections
users = database.users

# Create indexes for better performance
async def create_indexes():
    # Users collection indexes
    await users.create_index("email", unique=True)
    await users.create_index("uid")
    await users.create_index("status")
    await users.create_index("type")

# Initialize database
async def init_db():
    await create_indexes()
    print("Database initialized successfully!") 