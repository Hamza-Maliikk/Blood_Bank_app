from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Global database client
client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    """Create database connection."""
    global client, database
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        database = client[settings.MONGODB_DATABASE]
        
        # Test the connection
        await client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection."""
    global client
    if client:
        client.close()
        logger.info("Disconnected from MongoDB")


async def create_indexes():
    """Create database indexes for better performance."""
    try:
        # Users collection indexes
        await database.users.create_index("email", unique=True)
        await database.users.create_index("uid", unique=True)
        await database.users.create_index("city")
        await database.users.create_index("available")
        await database.users.create_index("bloodGroup")
        
        # Requests collection indexes
        await database.requests.create_index("id", unique=True)
        await database.requests.create_index("createdBy")
        await database.requests.create_index("requestedTo")
        await database.requests.create_index("status")
        await database.requests.create_index("city")
        await database.requests.create_index("requiredBloodGroup")
        await database.requests.create_index("createdAt")
        
        # Compound indexes for common queries
        await database.requests.create_index([
            ("status", 1),
            ("city", 1),
            ("requiredBloodGroup", 1)
        ])
        
        await database.requests.create_index([
            ("requestedTo", 1),
            ("status", 1)
        ])
        
        # Donations collection indexes
        await database.donations.create_index("userId")
        await database.donations.create_index("requestId")
        await database.donations.create_index("status")
        
        # Money donations collection indexes
        await database.money_donations.create_index("uid")
        await database.money_donations.create_index("stripePaymentId", unique=True)
        await database.money_donations.create_index("createdAt")
        
        # Comments collection indexes
        await database.comments.create_index("requestId")
        await database.comments.create_index("uid")
        await database.comments.create_index("createdAt")
        
        # Notifications collection indexes
        await database.notifications.create_index("uid")
        await database.notifications.create_index("read")
        await database.notifications.create_index("createdAt")
        
        # Chat sessions collection indexes
        await database.chat_sessions.create_index("uid")
        await database.chat_sessions.create_index("createdAt")
        
        # Chat messages collection indexes
        await database.chat_messages.create_index("sessionId")
        await database.chat_messages.create_index("createdAt")
        
        # File attachments collection indexes
        await database.file_attachments.create_index("uploadedBy")
        await database.file_attachments.create_index("createdAt")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        # Don't raise here as the app can still work without indexes


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    if database is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return database


def get_client() -> AsyncIOMotorClient:
    """Get MongoDB client instance."""
    if client is None:
        raise RuntimeError("MongoDB client not initialized. Call connect_to_mongo() first.")
    return client
