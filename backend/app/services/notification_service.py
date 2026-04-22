from typing import Optional, List, Dict, Any
from datetime import datetime
from app.repositories.factory import get_notification_repository
from app.domain.entities import Notification
import logging
import uuid
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Notification service for push notifications and in-app notifications."""
    
    def __init__(self):
        self.notification_repo = get_notification_repository()
    
    async def create_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create a new notification."""
        try:
            # Generate notification ID
            notification_id = str(uuid.uuid4())
            
            # Create notification
            notification = Notification(
                id=notification_id,
                uid=user_id,
                type=notification_type,
                title=title,
                message=message,
                data=data
            )
            
            created_notification = await self.notification_repo.create_notification(notification)
            
            # Send push notification via OneSignal
            await self._send_push_notification(user_id, title, message, data)
            
            logger.info(f"Created notification: {notification_id}")
            return created_notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            raise
    
    async def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        try:
            notification = await self.notification_repo.get_notification_by_id(notification_id)
            if notification:
                logger.info(f"Retrieved notification: {notification_id}")
            return notification
        except Exception as e:
            logger.error(f"Error getting notification by ID: {e}")
            raise
    
    async def mark_notification_as_read(self, notification_id: str) -> bool:
        """Mark notification as read."""
        try:
            success = await self.notification_repo.mark_as_read(notification_id)
            if success:
                logger.info(f"Marked notification as read: {notification_id}")
            return success
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            raise
    
    async def mark_all_notifications_as_read(self, user_id: str) -> int:
        """Mark all user notifications as read."""
        try:
            count = await self.notification_repo.mark_all_as_read(user_id)
            logger.info(f"Marked {count} notifications as read for user {user_id}")
            return count
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")
            raise
    
    async def list_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False
    ) -> List[Notification]:
        """List user notifications."""
        try:
            notifications = await self.notification_repo.list_user_notifications(
                user_id, unread_only
            )
            logger.info(f"Found {len(notifications)} notifications for user {user_id}")
            return notifications
        except Exception as e:
            logger.error(f"Error listing user notifications: {e}")
            raise
    
    async def send_request_notification(
        self,
        donor_id: str,
        request_id: str,
        patient_name: str,
        blood_group: str,
        city: str
    ) -> Notification:
        """Send notification for new blood request."""
        try:
            title = "New Blood Request"
            message = f"{patient_name} needs {blood_group} blood in {city}"
            data = {
                "type": "blood_request",
                "request_id": request_id,
                "action": "view_request"
            }
            
            notification = await self.create_notification(
                donor_id, "blood_request", title, message, data
            )
            
            logger.info(f"Sent request notification to donor {donor_id}")
            return notification
            
        except Exception as e:
            logger.error(f"Error sending request notification: {e}")
            raise
    
    async def send_request_response_notification(
        self,
        patient_id: str,
        request_id: str,
        donor_name: str,
        response: str  # "accepted" or "rejected"
    ) -> Notification:
        """Send notification for request response."""
        try:
            title = f"Request {response.title()}"
            message = f"{donor_name} has {response} your blood request"
            data = {
                "type": "request_response",
                "request_id": request_id,
                "response": response,
                "action": "view_request"
            }
            
            notification = await self.create_notification(
                patient_id, "request_response", title, message, data
            )
            
            logger.info(f"Sent response notification to patient {patient_id}")
            return notification
            
        except Exception as e:
            logger.error(f"Error sending response notification: {e}")
            raise
    
    async def send_donation_confirmation_notification(
        self,
        donor_id: str,
        amount: float,
        currency: str = "PKR"
    ) -> Notification:
        """Send money donation confirmation notification."""
        try:
            title = "Donation Confirmed"
            message = f"Thank you for your donation of {amount} {currency}"
            data = {
                "type": "donation_confirmation",
                "amount": amount,
                "currency": currency,
                "action": "view_donations"
            }
            
            notification = await self.create_notification(
                donor_id, "donation_confirmation", title, message, data
            )
            
            logger.info(f"Sent donation confirmation to donor {donor_id}")
            return notification
            
        except Exception as e:
            logger.error(f"Error sending donation confirmation: {e}")
            raise
    
    async def send_system_announcement(
        self,
        user_ids: List[str],
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> List[Notification]:
        """Send system announcement to multiple users."""
        try:
            notifications = []
            for user_id in user_ids:
                notification = await self.create_notification(
                    user_id, "system_announcement", title, message, data
                )
                notifications.append(notification)
            
            logger.info(f"Sent system announcement to {len(user_ids)} users")
            return notifications
            
        except Exception as e:
            logger.error(f"Error sending system announcement: {e}")
            raise
    
    async def _send_push_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send push notification via OneSignal."""
        try:
            if not settings.ONESIGNAL_APP_ID or not settings.ONESIGNAL_API_KEY:
                logger.warning("OneSignal not configured, skipping push notification")
                return False
            
            # OneSignal API endpoint
            url = "https://onesignal.com/api/v1/notifications"
            
            # Prepare notification payload
            payload = {
                "app_id": settings.ONESIGNAL_APP_ID,
                "include_external_user_ids": [user_id],
                "headings": {"en": title},
                "contents": {"en": message},
                "data": data or {},
                "small_icon": "ic_notification",
                "large_icon": "ic_launcher"
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic {settings.ONESIGNAL_API_KEY}"
            }
            
            # Send notification
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            logger.info(f"Push notification sent successfully to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return False
