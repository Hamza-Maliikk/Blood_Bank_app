from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from app.domain.entities import (
    UserProfile, BloodRequest, Donation, Comment, MoneyDonation,
    Notification, ChatSession, ChatMessage, FileAttachment
)


class BaseRepository(ABC):
    """Base repository interface with common CRUD operations."""
    
    @abstractmethod
    async def create(self, entity: Any) -> Any:
        """Create a new entity."""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[Any]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def update(self, entity_id: str, update_data: Dict[str, Any]) -> Optional[Any]:
        """Update entity by ID."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete entity by ID."""
        pass
    
    @abstractmethod
    async def list(self, filters: Optional[Dict[str, Any]] = None, 
                  skip: int = 0, limit: int = 100) -> List[Any]:
        """List entities with optional filters."""
        pass


class IUserRepository(ABC):
    """User repository interface."""
    
    @abstractmethod
    async def create_user(self, user: UserProfile, password_hash: str) -> UserProfile:
        """Create a new user with password."""
        pass
    
    @abstractmethod
    async def get_user_by_id(self, uid: str) -> Optional[UserProfile]:
        """Get user by UID."""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        """Get user by email."""
        pass
    
    @abstractmethod
    async def update_user(self, uid: str, update_data: Dict[str, Any]) -> Optional[UserProfile]:
        """Update user."""
        pass
    
    @abstractmethod
    async def get_password_hash(self, uid: str) -> Optional[str]:
        """Get user's password hash."""
        pass
    
    @abstractmethod
    async def list_available_donors(self, filters: Optional[Dict[str, Any]] = None) -> List[UserProfile]:
        """List available donors with filters."""
        pass
    
    @abstractmethod
    async def update_availability(self, uid: str, available: bool) -> bool:
        """Update donor availability."""
        pass
    
    @abstractmethod
    async def list_all_users(self, skip: int = 0, limit: int = 100) -> List[UserProfile]:
        """List all users (admin only)."""
        pass


class IRequestRepository(ABC):
    """Blood request repository interface."""
    
    @abstractmethod
    async def create_request(self, request: BloodRequest) -> BloodRequest:
        """Create a new blood request."""
        pass
    
    @abstractmethod
    async def get_request_by_id(self, request_id: str) -> Optional[BloodRequest]:
        """Get request by ID."""
        pass
    
    @abstractmethod
    async def update_request(self, request_id: str, update_data: Dict[str, Any]) -> Optional[BloodRequest]:
        """Update request."""
        pass
    
    @abstractmethod
    async def list_requests(self, filters: Optional[Dict[str, Any]] = None,
                           skip: int = 0, limit: int = 100) -> List[BloodRequest]:
        """List requests with filters."""
        pass
    
    @abstractmethod
    async def list_user_requests(self, user_id: str) -> List[BloodRequest]:
        """List requests created by user."""
        pass
    
    @abstractmethod
    async def list_donor_inbox(self, donor_id: str) -> Dict[str, List[BloodRequest]]:
        """Get donor inbox (targeted + discoverable requests)."""
        pass
    
    @abstractmethod
    async def get_donor_stats(self, donor_id: str) -> Dict[str, int]:
        """Get donor statistics."""
        pass


class IDonationRepository(ABC):
    """Donation repository interface."""
    
    @abstractmethod
    async def create_donation(self, donation: Donation) -> Donation:
        """Create a new blood donation."""
        pass
    
    @abstractmethod
    async def get_donation_by_id(self, donation_id: str) -> Optional[Donation]:
        """Get donation by ID."""
        pass
    
    @abstractmethod
    async def update_donation(self, donation_id: str, update_data: Dict[str, Any]) -> Optional[Donation]:
        """Update donation."""
        pass
    
    @abstractmethod
    async def list_user_donations(self, user_id: str) -> List[Donation]:
        """List user's blood donations."""
        pass
    
    @abstractmethod
    async def create_money_donation(self, donation: MoneyDonation) -> MoneyDonation:
        """Create a new money donation."""
        pass
    
    @abstractmethod
    async def get_money_donation_by_id(self, donation_id: str) -> Optional[MoneyDonation]:
        """Get money donation by ID."""
        pass
    
    @abstractmethod
    async def list_user_money_donations(self, user_id: str) -> List[MoneyDonation]:
        """List user's money donations."""
        pass
    
    @abstractmethod
    async def get_money_donation_by_stripe_id(self, stripe_payment_id: str) -> Optional[MoneyDonation]:
        """Get money donation by Stripe payment ID."""
        pass
    
    @abstractmethod
    async def list_money_donations(self, skip: int = 0, limit: int = 100) -> List[MoneyDonation]:
        """List all money donations with pagination."""
        pass


class ICommentRepository(ABC):
    """Comment repository interface."""
    
    @abstractmethod
    async def create_comment(self, comment: Comment) -> Comment:
        """Create a new comment."""
        pass
    
    @abstractmethod
    async def get_comment_by_id(self, comment_id: str) -> Optional[Comment]:
        """Get comment by ID."""
        pass
    
    @abstractmethod
    async def delete_comment(self, comment_id: str) -> bool:
        """Delete comment."""
        pass
    
    @abstractmethod
    async def list_request_comments(self, request_id: str) -> List[Comment]:
        """List comments for a request."""
        pass


class INotificationRepository(ABC):
    """Notification repository interface."""
    
    @abstractmethod
    async def create_notification(self, notification: Notification) -> Notification:
        """Create a new notification."""
        pass
    
    @abstractmethod
    async def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        pass
    
    @abstractmethod
    async def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read."""
        pass
    
    @abstractmethod
    async def list_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Notification]:
        """List user notifications."""
        pass
    
    @abstractmethod
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all user notifications as read."""
        pass


class IChatRepository(ABC):
    """Chat repository interface."""
    
    @abstractmethod
    async def create_session(self, session: ChatSession) -> ChatSession:
        """Create a new chat session."""
        pass
    
    @abstractmethod
    async def get_session_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID."""
        pass
    
    @abstractmethod
    async def list_user_sessions(self, user_id: str) -> List[ChatSession]:
        """List user's chat sessions."""
        pass
    
    @abstractmethod
    async def create_message(self, message: ChatMessage) -> ChatMessage:
        """Create a new chat message."""
        pass
    
    @abstractmethod
    async def get_message_by_id(self, message_id: str) -> Optional[ChatMessage]:
        """Get chat message by ID."""
        pass
    
    @abstractmethod
    async def list_session_messages(self, session_id: str) -> List[ChatMessage]:
        """List messages in a session."""
        pass
    
    @abstractmethod
    async def create_file_attachment(self, attachment: FileAttachment) -> FileAttachment:
        """Create a new file attachment."""
        pass
    
    @abstractmethod
    async def get_file_attachment_by_id(self, attachment_id: str) -> Optional[FileAttachment]:
        """Get file attachment by ID."""
        pass
