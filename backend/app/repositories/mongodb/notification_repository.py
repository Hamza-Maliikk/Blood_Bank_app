from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.repositories.base import INotificationRepository
from app.domain.entities import Notification
import logging

logger = logging.getLogger(__name__)


class MongoNotificationRepository(INotificationRepository):
    """MongoDB implementation of notification repository."""
    
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.notifications
    
    async def create_notification(self, notification: Notification) -> Notification:
        """Create a new notification."""
        try:
            notification_dict = {
                "id": notification.id,
                "uid": notification.uid,
                "type": notification.type,
                "title": notification.title,
                "message": notification.message,
                "data": notification.data,
                "read": notification.read,
                "createdAt": notification.createdAt
            }
            
            # Remove None values
            notification_dict = {k: v for k, v in notification_dict.items() if v is not None}
            
            result = await self.collection.insert_one(notification_dict)
            if result.inserted_id:
                logger.info(f"Notification created successfully: {notification.id}")
                return notification
            else:
                raise Exception("Failed to create notification")
                
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            raise
    
    async def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        try:
            notification_doc = await self.collection.find_one({"id": notification_id})
            if notification_doc:
                return self._doc_to_notification(notification_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting notification by ID: {e}")
            raise
    
    async def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read."""
        try:
            result = await self.collection.update_one(
                {"id": notification_id},
                {"$set": {"read": True}}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Notification marked as read: {notification_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            raise
    
    async def list_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Notification]:
        """List user notifications."""
        try:
            query = {"uid": user_id}
            if unread_only:
                query["read"] = False
            
            cursor = self.collection.find(query).sort("createdAt", -1)
            notifications = []
            async for doc in cursor:
                notifications.append(self._doc_to_notification(doc))
            
            logger.info(f"Found {len(notifications)} notifications for user {user_id}")
            return notifications
            
        except Exception as e:
            logger.error(f"Error listing user notifications: {e}")
            raise
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all user notifications as read."""
        try:
            result = await self.collection.update_many(
                {"uid": user_id, "read": False},
                {"$set": {"read": True}}
            )
            
            count = result.modified_count
            logger.info(f"Marked {count} notifications as read for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")
            raise
    
    def _doc_to_notification(self, doc: Dict[str, Any]) -> Notification:
        """Convert MongoDB document to Notification."""
        return Notification(
            id=doc["id"],
            uid=doc["uid"],
            type=doc["type"],
            title=doc["title"],
            message=doc["message"],
            data=doc.get("data"),
            read=doc.get("read", False),
            createdAt=doc.get("createdAt")
        )
