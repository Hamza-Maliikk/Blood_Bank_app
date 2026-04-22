from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.repositories.base import IUserRepository
from app.domain.entities import UserProfile
import logging

logger = logging.getLogger(__name__)


class MongoUserRepository(IUserRepository):
    """MongoDB implementation of user repository."""
    
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.users
    
    async def create_user(self, user: UserProfile, password_hash: str) -> UserProfile:
        """Create a new user with password."""
        try:
            user_dict = {
                "uid": user.uid,
                "name": user.name,
                "email": user.email,
                "gender": user.gender,
                "bloodGroup": user.bloodGroup,
                "city": user.city,
                "cnic": user.cnic,
                "phone": user.phone,
                "available": user.available,
                "mode": user.mode,
                "role": user.role,
                "themePreference": user.themePreference,
                "locationLat": user.locationLat,
                "locationLng": user.locationLng,
                "password_hash": password_hash,
                "createdAt": user.createdAt,
                "updatedAt": user.updatedAt
            }
            
            # Remove None values
            user_dict = {k: v for k, v in user_dict.items() if v is not None}
            
            result = await self.collection.insert_one(user_dict)
            if result.inserted_id:
                logger.info(f"User created successfully: {user.uid}")
                return user
            else:
                raise Exception("Failed to create user")
                
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_user_by_id(self, uid: str) -> Optional[UserProfile]:
        """Get user by UID."""
        try:
            user_doc = await self.collection.find_one({"uid": uid})
            if user_doc:
                return self._doc_to_user(user_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        """Get user by email."""
        try:
            user_doc = await self.collection.find_one({"email": email})
            if user_doc:
                return self._doc_to_user(user_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise
    
    async def update_user(self, uid: str, update_data: Dict[str, Any]) -> Optional[UserProfile]:
        """Update user."""
        try:
            update_data["updatedAt"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"uid": uid},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                updated_user = await self.get_user_by_id(uid)
                logger.info(f"User updated successfully: {uid}")
                return updated_user
            return None
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise
    
    async def get_password_hash(self, uid: str) -> Optional[str]:
        """Get user's password hash."""
        try:
            user_doc = await self.collection.find_one(
                {"uid": uid},
                {"password_hash": 1}
            )
            if user_doc:
                return user_doc.get("password_hash")
            return None
        except Exception as e:
            logger.error(f"Error getting password hash: {e}")
            raise
    
    async def list_available_donors(self, filters: Optional[Dict[str, Any]] = None) -> List[UserProfile]:
        """List available donors with filters."""
        try:
            query = {"available": True, "mode": "donor"}
            
            if filters:
                if "bloodGroup" in filters:
                    query["bloodGroup"] = filters["bloodGroup"]
                if "city" in filters:
                    query["city"] = filters["city"]
                if "gender" in filters:
                    query["gender"] = filters["gender"]
            
            cursor = self.collection.find(query)
            users = []
            async for doc in cursor:
                users.append(self._doc_to_user(doc))
            
            logger.info(f"Found {len(users)} available donors")
            return users
            
        except Exception as e:
            logger.error(f"Error listing available donors: {e}")
            raise
    
    async def update_availability(self, uid: str, available: bool) -> bool:
        """Update donor availability."""
        try:
            result = await self.collection.update_one(
                {"uid": uid},
                {
                    "$set": {
                        "available": available,
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Availability updated for user {uid}: {available}")
            return success
            
        except Exception as e:
            logger.error(f"Error updating availability: {e}")
            raise
    
    async def list_all_users(self, skip: int = 0, limit: int = 100) -> List[UserProfile]:
        """List all users (admin only)."""
        try:
            cursor = self.collection.find().skip(skip).limit(limit)
            users = []
            async for doc in cursor:
                users.append(self._doc_to_user(doc))
            
            logger.info(f"Found {len(users)} users")
            return users
            
        except Exception as e:
            logger.error(f"Error listing all users: {e}")
            raise
    
    def _doc_to_user(self, doc: Dict[str, Any]) -> UserProfile:
        """Convert MongoDB document to UserProfile."""
        return UserProfile(
            uid=doc["uid"],
            name=doc["name"],
            email=doc.get("email"),
            gender=doc.get("gender"),
            bloodGroup=doc.get("bloodGroup"),
            city=doc.get("city"),
            cnic=doc.get("cnic"),
            phone=doc.get("phone"),
            available=doc.get("available", True),
            mode=doc.get("mode", "patient"),
            role=doc.get("role", "user"),
            themePreference=doc.get("themePreference", "system"),
            locationLat=doc.get("locationLat"),
            locationLng=doc.get("locationLng"),
            createdAt=doc.get("createdAt"),
            updatedAt=doc.get("updatedAt")
        )
