#!/usr/bin/env python3
"""
Development seeder script for MongoDB.
Creates realistic sample data for development and testing.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
import uuid
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'bloodbank')

# Password hashing
def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    # Ensure password is not longer than 72 bytes for bcrypt
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

class DatabaseSeeder:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        
    async def initialize(self):
        """Initialize MongoDB connection."""
        try:
            self.mongo_client = AsyncIOMotorClient(MONGODB_URI)
            self.db = self.mongo_client[MONGODB_DATABASE]
            await self.mongo_client.admin.command('ping')
            logger.info("MongoDB connected successfully")
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            raise
    
    async def close(self):
        """Close database connection."""
        if self.mongo_client:
            self.mongo_client.close()
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        # Ensure password is not longer than 72 bytes for bcrypt
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    async def clear_database(self):
        """Clear all collections."""
        logger.info("Clearing existing data...")
        
        collections = [
            'users', 'requests', 'donations', 'money_donations',
            'comments', 'notifications', 'chat_sessions', 'chat_messages',
            'file_attachments'
        ]
        
        for collection_name in collections:
            await self.db[collection_name].delete_many({})
            logger.info(f"Cleared {collection_name} collection")
    
    async def seed_users(self) -> List[str]:
        """Seed users collection with sample data."""
        logger.info("Seeding users...")
        
        users_data = [
            {
                "uid": "admin-001",
                "name": "Admin User",
                "email": "admin@bloodbank.com",
                "gender": "Male",
                "bloodGroup": "O+",
                "city": "Karachi",
                "cnic": "12345-1234567-1",
                "phone": "+92-300-1234567",
                "available": True,
                "mode": "donor",
                "role": "admin",
                "themePreference": "system",
                "password_hash": self.get_password_hash("admin123"),
                "createdAt": datetime.utcnow() - timedelta(days=30),
                "updatedAt": datetime.utcnow()
            },
            {
                "uid": "patient-001",
                "name": "Ahmed Ali",
                "email": "ahmed@example.com",
                "gender": "Male",
                "bloodGroup": "A+",
                "city": "Lahore",
                "cnic": "12345-1234567-2",
                "phone": "+92-300-1234568",
                "available": False,
                "mode": "patient",
                "role": "user",
                "themePreference": "light",
                "password_hash": self.get_password_hash("pass123"),
                "createdAt": datetime.utcnow() - timedelta(days=25),
                "updatedAt": datetime.utcnow()
            },
            {
                "uid": "donor-001",
                "name": "Fatima Khan",
                "email": "fatima@example.com",
                "gender": "Female",
                "bloodGroup": "O+",
                "city": "Karachi",
                "cnic": "12345-1234567-3",
                "phone": "+92-300-1234569",
                "available": True,
                "mode": "donor",
                "role": "user",
                "themePreference": "dark",
                "password_hash": self.get_password_hash("pass123"),
                "createdAt": datetime.utcnow() - timedelta(days=20),
                "updatedAt": datetime.utcnow()
            },
            {
                "uid": "donor-002",
                "name": "Muhammad Hassan",
                "email": "hassan@example.com",
                "gender": "Male",
                "bloodGroup": "B+",
                "city": "Islamabad",
                "cnic": "12345-1234567-4",
                "phone": "+92-300-1234570",
                "available": True,
                "mode": "donor",
                "role": "user",
                "themePreference": "system",
                "password_hash": self.get_password_hash("pass123"),
                "createdAt": datetime.utcnow() - timedelta(days=18),
                "updatedAt": datetime.utcnow()
            },
            {
                "uid": "donor-003",
                "name": "Ayesha Malik",
                "email": "ayesha@example.com",
                "gender": "Female",
                "bloodGroup": "AB+",
                "city": "Lahore",
                "cnic": "12345-1234567-5",
                "phone": "+92-300-1234571",
                "available": True,
                "mode": "donor",
                "role": "user",
                "themePreference": "light",
                "password_hash": self.get_password_hash("pass123"),
                "createdAt": datetime.utcnow() - timedelta(days=15),
                "updatedAt": datetime.utcnow()
            },
            {
                "uid": "donor-004",
                "name": "Ali Raza",
                "email": "ali@example.com",
                "gender": "Male",
                "bloodGroup": "A-",
                "city": "Karachi",
                "cnic": "12345-1234567-6",
                "phone": "+92-300-1234572",
                "available": False,
                "mode": "donor",
                "role": "user",
                "themePreference": "dark",
                "password_hash": self.get_password_hash("pass123"),
                "createdAt": datetime.utcnow() - timedelta(days=12),
                "updatedAt": datetime.utcnow()
            },
            {
                "uid": "donor-005",
                "name": "Sara Ahmed",
                "email": "sara@example.com",
                "gender": "Female",
                "bloodGroup": "O-",
                "city": "Rawalpindi",
                "cnic": "12345-1234567-7",
                "phone": "+92-300-1234573",
                "available": True,
                "mode": "donor",
                "role": "user",
                "themePreference": "system",
                "password_hash": self.get_password_hash("pass123"),
                "createdAt": datetime.utcnow() - timedelta(days=10),
                "updatedAt": datetime.utcnow()
            },
            {
                "uid": "donor-006",
                "name": "Hassan Shah",
                "email": "hassan.shah@example.com",
                "gender": "Male",
                "bloodGroup": "B-",
                "city": "Faisalabad",
                "cnic": "12345-1234567-8",
                "phone": "+92-300-1234574",
                "available": True,
                "mode": "donor",
                "role": "user",
                "themePreference": "light",
                "password_hash": self.get_password_hash("pass123"),
                "createdAt": datetime.utcnow() - timedelta(days=8),
                "updatedAt": datetime.utcnow()
            }
        ]
        
        await self.db.users.insert_many(users_data)
        logger.info(f"Seeded {len(users_data)} users")
        
        return [user["uid"] for user in users_data]
    
    async def seed_requests(self, user_ids: List[str]) -> List[str]:
        """Seed requests collection with sample data."""
        logger.info("Seeding requests...")
        
        requests_data = [
            {
                "id": "req-001",
                "createdBy": "patient-001",
                "patientName": "Ahmed Ali",
                "requiredBloodGroup": "O+",
                "city": "Lahore",
                "gender": "Male",
                "hospital": "Services Hospital",
                "locationAddress": "Services Hospital, Lahore",
                "locationLat": 31.5204,
                "locationLng": 74.3587,
                "unitsRequired": 2,
                "neededBy": datetime.utcnow() + timedelta(days=3),
                "notes": "Urgent blood requirement for surgery",
                "requestedTo": "donor-001",
                "status": "pending",
                "createdAt": datetime.utcnow() - timedelta(days=2)
            },
            {
                "id": "req-002",
                "createdBy": "patient-001",
                "patientName": "Sara Khan",
                "requiredBloodGroup": "A+",
                "city": "Karachi",
                "gender": "Female",
                "hospital": "Aga Khan Hospital",
                "locationAddress": "Aga Khan Hospital, Karachi",
                "locationLat": 24.8607,
                "locationLng": 67.0011,
                "unitsRequired": 1,
                "neededBy": datetime.utcnow() + timedelta(days=5),
                "notes": "Blood needed for emergency",
                "requestedTo": None,
                "status": "open",
                "createdAt": datetime.utcnow() - timedelta(days=1)
            },
            {
                "id": "req-003",
                "createdBy": "admin-001",
                "patientName": "Muhammad Ali",
                "requiredBloodGroup": "B+",
                "city": "Islamabad",
                "gender": "Male",
                "hospital": "PIMS Hospital",
                "locationAddress": "PIMS Hospital, Islamabad",
                "locationLat": 33.6844,
                "locationLng": 73.0479,
                "unitsRequired": 3,
                "neededBy": datetime.utcnow() + timedelta(days=7),
                "notes": "Multiple units required for major surgery",
                "requestedTo": "donor-002",
                "status": "accepted",
                "createdAt": datetime.utcnow() - timedelta(hours=6)
            }
        ]
        
        await self.db.requests.insert_many(requests_data)
        logger.info(f"Seeded {len(requests_data)} requests")
        
        return [request["id"] for request in requests_data]
    
    async def seed_donations(self, user_ids: List[str], request_ids: List[str]):
        """Seed donations collection with sample data."""
        logger.info("Seeding donations...")
        
        donations_data = [
            {
                "id": "don-001",
                "userId": "donor-001",
                "requestId": "req-001",
                "status": "pending",
                "date": datetime.utcnow() - timedelta(hours=2)
            },
            {
                "id": "don-002",
                "userId": "donor-002",
                "requestId": "req-003",
                "status": "pending",
                "date": datetime.utcnow() - timedelta(hours=1)
            },
            {
                "id": "don-003",
                "userId": "donor-003",
                "requestId": "req-002",
                "status": "donated",
                "date": datetime.utcnow() - timedelta(days=1)
            }
        ]
        
        await self.db.donations.insert_many(donations_data)
        logger.info(f"Seeded {len(donations_data)} donations")
    
    async def seed_money_donations(self, user_ids: List[str]):
        """Seed money donations collection with sample data."""
        logger.info("Seeding money donations...")
        
        money_donations_data = [
            {
                "id": "money-001",
                "uid": "donor-001",
                "amount": 5000.0,
                "currency": "PKR",
                "purpose": "Emergency fund",
                "stripePaymentId": "pi_test_123456789",
                "stripeSessionId": "cs_test_123456789",
                "receiptUrl": "https://example.com/receipt/001",
                "createdAt": datetime.utcnow() - timedelta(days=5)
            },
            {
                "id": "money-002",
                "uid": "donor-002",
                "amount": 10000.0,
                "currency": "PKR",
                "purpose": "General donation",
                "stripePaymentId": "pi_test_987654321",
                "stripeSessionId": "cs_test_987654321",
                "receiptUrl": "https://example.com/receipt/002",
                "createdAt": datetime.utcnow() - timedelta(days=3)
            },
            {
                "id": "money-003",
                "uid": "donor-003",
                "amount": 2500.0,
                "currency": "PKR",
                "purpose": "Blood bank support",
                "stripePaymentId": "pi_test_456789123",
                "stripeSessionId": "cs_test_456789123",
                "receiptUrl": "https://example.com/receipt/003",
                "createdAt": datetime.utcnow() - timedelta(days=1)
            }
        ]
        
        await self.db.money_donations.insert_many(money_donations_data)
        logger.info(f"Seeded {len(money_donations_data)} money donations")
    
    async def seed_comments(self, request_ids: List[str], user_ids: List[str]):
        """Seed comments collection with sample data."""
        logger.info("Seeding comments...")
        
        comments_data = [
            {
                "id": "comment-001",
                "requestId": "req-001",
                "uid": "donor-001",
                "text": "I can help with this request. Please contact me.",
                "createdAt": datetime.utcnow() - timedelta(hours=3)
            },
            {
                "id": "comment-002",
                "requestId": "req-001",
                "uid": "patient-001",
                "text": "Thank you for your willingness to help!",
                "createdAt": datetime.utcnow() - timedelta(hours=2)
            },
            {
                "id": "comment-003",
                "requestId": "req-002",
                "uid": "donor-003",
                "text": "I'm available for this blood donation.",
                "createdAt": datetime.utcnow() - timedelta(hours=1)
            },
            {
                "id": "comment-004",
                "requestId": "req-003",
                "uid": "donor-002",
                "text": "I'll be there at the scheduled time.",
                "createdAt": datetime.utcnow() - timedelta(minutes=30)
            }
        ]
        
        await self.db.comments.insert_many(comments_data)
        logger.info(f"Seeded {len(comments_data)} comments")
    
    async def seed_notifications(self, user_ids: List[str]):
        """Seed notifications collection with sample data."""
        logger.info("Seeding notifications...")
        
        notifications_data = [
            {
                "id": "notif-001",
                "uid": "donor-001",
                "type": "blood_request",
                "title": "New Blood Request",
                "message": "Ahmed Ali needs O+ blood in Lahore",
                "data": {
                    "request_id": "req-001",
                    "action": "view_request"
                },
                "read": False,
                "createdAt": datetime.utcnow() - timedelta(hours=2)
            },
            {
                "id": "notif-002",
                "uid": "patient-001",
                "type": "request_response",
                "title": "Request Accepted",
                "message": "Fatima Khan has accepted your blood request",
                "data": {
                    "request_id": "req-001",
                    "response": "accepted",
                    "action": "view_request"
                },
                "read": True,
                "createdAt": datetime.utcnow() - timedelta(hours=1)
            },
            {
                "id": "notif-003",
                "uid": "donor-002",
                "type": "donation_confirmation",
                "title": "Donation Confirmed",
                "message": "Thank you for your donation of PKR 10,000",
                "data": {
                    "amount": 10000,
                    "currency": "PKR",
                    "action": "view_donations"
                },
                "read": False,
                "createdAt": datetime.utcnow() - timedelta(minutes=30)
            },
            {
                "id": "notif-004",
                "uid": "donor-003",
                "type": "system_announcement",
                "title": "Platform Update",
                "message": "New features have been added to the platform",
                "data": {
                    "action": "view_announcements"
                },
                "read": False,
                "createdAt": datetime.utcnow() - timedelta(minutes=15)
            }
        ]
        
        await self.db.notifications.insert_many(notifications_data)
        logger.info(f"Seeded {len(notifications_data)} notifications")
    
    async def seed_chat_sessions(self, user_ids: List[str]) -> List[str]:
        """Seed chat sessions collection with sample data."""
        logger.info("Seeding chat sessions...")
        
        chat_sessions_data = [
            {
                "id": "chat-001",
                "uid": "patient-001",
                "createdAt": datetime.utcnow() - timedelta(days=2),
                "updatedAt": datetime.utcnow() - timedelta(hours=1)
            },
            {
                "id": "chat-002",
                "uid": "donor-001",
                "createdAt": datetime.utcnow() - timedelta(days=1),
                "updatedAt": datetime.utcnow() - timedelta(minutes=30)
            },
            {
                "id": "chat-003",
                "uid": "donor-002",
                "createdAt": datetime.utcnow() - timedelta(hours=6),
                "updatedAt": datetime.utcnow() - timedelta(minutes=15)
            }
        ]
        
        await self.db.chat_sessions.insert_many(chat_sessions_data)
        logger.info(f"Seeded {len(chat_sessions_data)} chat sessions")
        
        return [session["id"] for session in chat_sessions_data]
    
    async def seed_chat_messages(self, session_ids: List[str]):
        """Seed chat messages collection with sample data."""
        logger.info("Seeding chat messages...")
        
        chat_messages_data = [
            {
                "id": "msg-001",
                "sessionId": "chat-001",
                "role": "user",
                "content": "Hello, I need help with blood donation information",
                "createdAt": datetime.utcnow() - timedelta(hours=2)
            },
            {
                "id": "msg-002",
                "sessionId": "chat-001",
                "role": "assistant",
                "content": "Hello! I'd be happy to help you with blood donation information. What specific questions do you have?",
                "createdAt": datetime.utcnow() - timedelta(hours=2, minutes=1)
            },
            {
                "id": "msg-003",
                "sessionId": "chat-001",
                "role": "user",
                "content": "What are the requirements for donating blood?",
                "createdAt": datetime.utcnow() - timedelta(hours=1, minutes=30)
            },
            {
                "id": "msg-004",
                "sessionId": "chat-001",
                "role": "assistant",
                "content": "To donate blood, you must be at least 17 years old, weigh at least 110 pounds, and be in good general health. You should also not have any infectious diseases and should not have donated blood in the last 56 days.",
                "createdAt": datetime.utcnow() - timedelta(hours=1, minutes=29)
            },
            {
                "id": "msg-005",
                "sessionId": "chat-002",
                "role": "user",
                "content": "How can I find blood requests in my area?",
                "createdAt": datetime.utcnow() - timedelta(minutes=45)
            },
            {
                "id": "msg-006",
                "sessionId": "chat-002",
                "role": "assistant",
                "content": "You can find blood requests in your area by using the donor inbox feature. It will show you both targeted requests (specifically sent to you) and discoverable requests (open requests in your area).",
                "createdAt": datetime.utcnow() - timedelta(minutes=44)
            }
        ]
        
        await self.db.chat_messages.insert_many(chat_messages_data)
        logger.info(f"Seeded {len(chat_messages_data)} chat messages")
    
    async def seed_all(self):
        """Seed all collections with sample data."""
        try:
            await self.initialize()
            
            logger.info("Starting database seeding...")
            
            # Clear existing data
            await self.clear_database()
            
            # Seed collections in order (respecting foreign key dependencies)
            user_ids = await self.seed_users()
            request_ids = await self.seed_requests(user_ids)
            await self.seed_donations(user_ids, request_ids)
            await self.seed_money_donations(user_ids)
            await self.seed_comments(request_ids, user_ids)
            await self.seed_notifications(user_ids)
            session_ids = await self.seed_chat_sessions(user_ids)
            await self.seed_chat_messages(session_ids)
            
            logger.info("Database seeding completed successfully!")
            
            # Print summary
            logger.info("\n=== SEEDING SUMMARY ===")
            logger.info(f"Users: {len(user_ids)}")
            logger.info(f"Requests: {len(request_ids)}")
            logger.info(f"Chat Sessions: {len(session_ids)}")
            logger.info("\n=== LOGIN CREDENTIALS ===")
            logger.info("Admin: admin@bloodbank.com / admin123")
            logger.info("Patient: ahmed@example.com / password123")
            logger.info("Donor: fatima@example.com / password123")
            
        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            raise
        finally:
            await self.close()

async def main():
    """Main seeding function."""
    seeder = DatabaseSeeder()
    await seeder.seed_all()

if __name__ == "__main__":
    asyncio.run(main())
