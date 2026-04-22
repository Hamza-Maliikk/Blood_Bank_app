from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.notification_service import NotificationService
from app.core.security import get_current_user, get_current_user_id, require_admin
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
notification_service = NotificationService()


# Request/Response Models
class NotificationSend(BaseModel):
    user_ids: List[str]
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None


@router.get("/")
async def list_user_notifications(
    unread_only: bool = Query(False, description="Show only unread notifications"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """List user notifications."""
    try:
        user_id = current_user["user_id"]
        notifications = await notification_service.list_user_notifications(
            user_id, unread_only
        )
        
        return {
            "success": True,
            "data": [notification.__dict__ for notification in notifications]
        }
        
    except Exception as e:
        logger.error(f"List user notifications error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list notifications"
        )


@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Mark notification as read."""
    try:
        success = await notification_service.mark_notification_as_read(notification_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return {
            "success": True,
            "message": "Notification marked as read"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mark notification as read error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read"
        )


@router.put("/mark-all-read")
async def mark_all_notifications_as_read(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Mark all user notifications as read."""
    try:
        user_id = current_user["user_id"]
        count = await notification_service.mark_all_notifications_as_read(user_id)
        
        return {
            "success": True,
            "message": f"Marked {count} notifications as read",
            "count": count
        }
        
    except Exception as e:
        logger.error(f"Mark all notifications as read error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark all notifications as read"
        )


@router.post("/send")
async def send_notification(
    notification_data: NotificationSend,
    admin_user: Dict[str, Any] = Depends(require_admin)
):
    """Send notification to multiple users (admin only)."""
    try:
        notifications = await notification_service.send_system_announcement(
            user_ids=notification_data.user_ids,
            title=notification_data.title,
            message=notification_data.message,
            data=notification_data.data
        )
        
        return {
            "success": True,
            "message": f"Notification sent to {len(notifications)} users",
            "count": len(notifications)
        }
        
    except Exception as e:
        logger.error(f"Send notification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send notification"
        )
