#!/usr/bin/env python3
"""
Data migration script from Firebase Realtime Database to MongoDB.
This script exports data from Firebase and imports it into MongoDB.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import firebase_admin
from firebase_admin import credentials, db
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Firebase configuration
FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH')
FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')

# MongoDB configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'bloodbank')

class FirebaseToMongoMigrator:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.firebase_app = None
        
    async def initialize(self):
        """Initialize Firebase and MongoDB connections."""
        try:
            # Initialize Firebase
            if FIREBASE_CREDENTIALS_PATH and FIREBASE_DATABASE_URL:
                cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
                self.firebase_app = firebase_admin.initialize_app(cred, {
                    'databaseURL': FIREBASE_DATABASE_URL
                })
                logger.info("Firebase initialized successfully")
            else:
                logger.warning("Firebase credentials not provided, skipping Firebase initialization")
            
            # Initialize MongoDB
            self.mongo_client = AsyncIOMotorClient(MONGODB_URI)
            self.db = self.mongo_client[MONGODB_DATABASE]
            await self.mongo_client.admin.command('ping')
            logger.info("MongoDB connected successfully")
            
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            raise
    
    async def close(self):
        """Close database connections."""
        if self.mongo_client:
            self.mongo_client.close()
        if self.firebase_app:
            firebase_admin.delete_app(self.firebase_app)
    
    def convert_timestamp(self, timestamp: Any) -> datetime:
        """Convert Firebase timestamp to MongoDB datetime."""
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp / 1000 if timestamp > 1e10 else timestamp)
        elif isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                return datetime.utcnow()
        else:
            return datetime.utcnow()
    
    async def migrate_users(self) -> Dict[str, str]:
        """Migrate users from Firebase to MongoDB."""
        logger.info("Starting users migration...")
        
        if not self.firebase_app:
            logger.warning("Firebase not initialized, skipping users migration")
            return {}
        
        # Get users from Firebase
        firebase_ref = db.reference('users')
        firebase_users = firebase_ref.get()
        
        if not firebase_users:
            logger.info("No users found in Firebase")
            return {}
        
        # Clear existing users in MongoDB
        await self.db.users.delete_many({})
        
        uid_mapping = {}
        users_to_insert = []
        
        for firebase_uid, user_data in firebase_users.items():
            if not user_data:
                continue
                
            # Convert Firebase user to MongoDB format
            mongo_user = {
                "uid": firebase_uid,
                "name": user_data.get("name", ""),
                "email": user_data.get("email"),
                "gender": user_data.get("gender"),
                "bloodGroup": user_data.get("bloodGroup"),
                "city": user_data.get("city"),
                "cnic": user_data.get("cnic"),
                "phone": user_data.get("phone"),
                "available": user_data.get("available", True),
                "mode": user_data.get("mode", "patient"),
                "role": user_data.get("role", "user"),
                "themePreference": user_data.get("themePreference", "system"),
                "createdAt": self.convert_timestamp(user_data.get("createdAt")),
                "updatedAt": self.convert_timestamp(user_data.get("updatedAt")),
                "password_hash": "migrated_user_password_hash"  # Placeholder
            }
            
            # Remove None values
            mongo_user = {k: v for k, v in mongo_user.items() if v is not None}
            users_to_insert.append(mongo_user)
            uid_mapping[firebase_uid] = firebase_uid
        
        # Insert users into MongoDB
        if users_to_insert:
            await self.db.users.insert_many(users_to_insert)
            logger.info(f"Migrated {len(users_to_insert)} users")
        
        return uid_mapping
    
    async def migrate_requests(self, uid_mapping: Dict[str, str]) -> Dict[str, str]:
        """Migrate blood requests from Firebase to MongoDB."""
        logger.info("Starting requests migration...")
        
        if not self.firebase_app:
            logger.warning("Firebase not initialized, skipping requests migration")
            return {}
        
        # Get requests from Firebase
        firebase_ref = db.reference('requests')
        firebase_requests = firebase_ref.get()
        
        if not firebase_requests:
            logger.info("No requests found in Firebase")
            return {}
        
        # Clear existing requests in MongoDB
        await self.db.requests.delete_many({})
        
        request_id_mapping = {}
        requests_to_insert = []
        
        for firebase_request_id, request_data in firebase_requests.items():
            if not request_data:
                continue
            
            # Convert Firebase request to MongoDB format
            mongo_request = {
                "id": firebase_request_id,
                "createdBy": request_data.get("createdBy"),
                "patientName": request_data.get("patientName", ""),
                "requiredBloodGroup": request_data.get("requiredBloodGroup", ""),
                "city": request_data.get("city", ""),
                "gender": request_data.get("gender"),
                "hospital": request_data.get("hospital"),
                "locationAddress": request_data.get("locationAddress"),
                "locationLat": request_data.get("locationLat"),
                "locationLng": request_data.get("locationLng"),
                "unitsRequired": request_data.get("unitsRequired"),
                "neededBy": self.convert_timestamp(request_data.get("neededBy")) if request_data.get("neededBy") else None,
                "notes": request_data.get("notes"),
                "requestedTo": request_data.get("requestedTo"),
                "status": request_data.get("status", "open"),
                "createdAt": self.convert_timestamp(request_data.get("createdAt"))
            }
            
            # Remove None values
            mongo_request = {k: v for k, v in mongo_request.items() if v is not None}
            requests_to_insert.append(mongo_request)
            request_id_mapping[firebase_request_id] = firebase_request_id
        
        # Insert requests into MongoDB
        if requests_to_insert:
            await self.db.requests.insert_many(requests_to_insert)
            logger.info(f"Migrated {len(requests_to_insert)} requests")
        
        return request_id_mapping
    
    async def migrate_donations(self, uid_mapping: Dict[str, str], request_id_mapping: Dict[str, str]):
        """Migrate donations from Firebase to MongoDB."""
        logger.info("Starting donations migration...")
        
        if not self.firebase_app:
            logger.warning("Firebase not initialized, skipping donations migration")
            return
        
        # Get donations from Firebase
        firebase_ref = db.reference('donations')
        firebase_donations = firebase_ref.get()
        
        if not firebase_donations:
            logger.info("No donations found in Firebase")
            return
        
        # Clear existing donations in MongoDB
        await self.db.donations.delete_many({})
        
        donations_to_insert = []
        
        for user_uid, user_donations in firebase_donations.items():
            if not user_donations:
                continue
            
            for donation_id, donation_data in user_donations.items():
                if not donation_data:
                    continue
                
                # Convert Firebase donation to MongoDB format
                mongo_donation = {
                    "id": donation_id,
                    "userId": user_uid,
                    "requestId": donation_data.get("requestId"),
                    "status": donation_data.get("status", "pending"),
                    "date": self.convert_timestamp(donation_data.get("date"))
                }
                
                # Remove None values
                mongo_donation = {k: v for k, v in mongo_donation.items() if v is not None}
                donations_to_insert.append(mongo_donation)
        
        # Insert donations into MongoDB
        if donations_to_insert:
            await self.db.donations.insert_many(donations_to_insert)
            logger.info(f"Migrated {len(donations_to_insert)} donations")
    
    async def migrate_money_donations(self, uid_mapping: Dict[str, str]):
        """Migrate money donations from Firebase to MongoDB."""
        logger.info("Starting money donations migration...")
        
        if not self.firebase_app:
            logger.warning("Firebase not initialized, skipping money donations migration")
            return
        
        # Get money donations from Firebase
        firebase_ref = db.reference('money_donations')
        firebase_money_donations = firebase_ref.get()
        
        if not firebase_money_donations:
            logger.info("No money donations found in Firebase")
            return
        
        # Clear existing money donations in MongoDB
        await self.db.money_donations.delete_many({})
        
        money_donations_to_insert = []
        
        for user_uid, user_money_donations in firebase_money_donations.items():
            if not user_money_donations:
                continue
            
            for donation_id, donation_data in user_money_donations.items():
                if not donation_data:
                    continue
                
                # Convert Firebase money donation to MongoDB format
                mongo_money_donation = {
                    "id": donation_id,
                    "uid": user_uid,
                    "amount": donation_data.get("amount", 0),
                    "currency": donation_data.get("currency", "PKR"),
                    "purpose": donation_data.get("purpose"),
                    "stripePaymentId": donation_data.get("stripePaymentId"),
                    "stripeSessionId": donation_data.get("stripeSessionId"),
                    "receiptUrl": donation_data.get("receiptUrl"),
                    "createdAt": self.convert_timestamp(donation_data.get("createdAt"))
                }
                
                # Remove None values
                mongo_money_donation = {k: v for k, v in mongo_money_donation.items() if v is not None}
                money_donations_to_insert.append(mongo_money_donation)
        
        # Insert money donations into MongoDB
        if money_donations_to_insert:
            await self.db.money_donations.insert_many(money_donations_to_insert)
            logger.info(f"Migrated {len(money_donations_to_insert)} money donations")
    
    async def migrate_comments(self, request_id_mapping: Dict[str, str]):
        """Migrate comments from Firebase to MongoDB."""
        logger.info("Starting comments migration...")
        
        if not self.firebase_app:
            logger.warning("Firebase not initialized, skipping comments migration")
            return
        
        # Get comments from Firebase
        firebase_ref = db.reference('comments')
        firebase_comments = firebase_ref.get()
        
        if not firebase_comments:
            logger.info("No comments found in Firebase")
            return
        
        # Clear existing comments in MongoDB
        await self.db.comments.delete_many({})
        
        comments_to_insert = []
        
        for request_id, request_comments in firebase_comments.items():
            if not request_comments:
                continue
            
            for comment_id, comment_data in request_comments.items():
                if not comment_data:
                    continue
                
                # Convert Firebase comment to MongoDB format
                mongo_comment = {
                    "id": comment_id,
                    "requestId": request_id,
                    "uid": comment_data.get("uid"),
                    "text": comment_data.get("text", ""),
                    "createdAt": self.convert_timestamp(comment_data.get("createdAt"))
                }
                
                # Remove None values
                mongo_comment = {k: v for k, v in mongo_comment.items() if v is not None}
                comments_to_insert.append(mongo_comment)
        
        # Insert comments into MongoDB
        if comments_to_insert:
            await self.db.comments.insert_many(comments_to_insert)
            logger.info(f"Migrated {len(comments_to_insert)} comments")
    
    async def migrate_all(self):
        """Migrate all data from Firebase to MongoDB."""
        try:
            await self.initialize()
            
            logger.info("Starting complete data migration...")
            
            # Migrate users first (required for foreign key references)
            uid_mapping = await self.migrate_users()
            
            # Migrate requests
            request_id_mapping = await self.migrate_requests(uid_mapping)
            
            # Migrate donations
            await self.migrate_donations(uid_mapping, request_id_mapping)
            
            # Migrate money donations
            await self.migrate_money_donations(uid_mapping)
            
            # Migrate comments
            await self.migrate_comments(request_id_mapping)
            
            logger.info("Data migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
        finally:
            await self.close()

async def main():
    """Main migration function."""
    migrator = FirebaseToMongoMigrator()
    await migrator.migrate_all()

if __name__ == "__main__":
    asyncio.run(main())
