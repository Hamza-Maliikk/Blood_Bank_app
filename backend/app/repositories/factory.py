from app.repositories.base import (
    IUserRepository, IRequestRepository, IDonationRepository,
    ICommentRepository, INotificationRepository, IChatRepository
)
from app.repositories.mongodb.user_repository import MongoUserRepository
from app.repositories.mongodb.request_repository import MongoRequestRepository
from app.repositories.mongodb.donation_repository import MongoDonationRepository
from app.repositories.mongodb.comment_repository import MongoCommentRepository
from app.repositories.mongodb.notification_repository import MongoNotificationRepository
from app.repositories.mongodb.chat_repository import MongoChatRepository
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RepositoryFactory:
    """Factory for creating repository instances."""
    
    _user_repo: IUserRepository = None
    _request_repo: IRequestRepository = None
    _donation_repo: IDonationRepository = None
    _comment_repo: ICommentRepository = None
    _notification_repo: INotificationRepository = None
    _chat_repo: IChatRepository = None
    
    @classmethod
    def get_user_repository(cls) -> IUserRepository:
        """Get user repository instance."""
        if cls._user_repo is None:
            cls._user_repo = MongoUserRepository()
            logger.info("Created MongoDB user repository")
        return cls._user_repo
    
    @classmethod
    def get_request_repository(cls) -> IRequestRepository:
        """Get request repository instance."""
        if cls._request_repo is None:
            cls._request_repo = MongoRequestRepository()
            logger.info("Created MongoDB request repository")
        return cls._request_repo
    
    @classmethod
    def get_donation_repository(cls) -> IDonationRepository:
        """Get donation repository instance."""
        if cls._donation_repo is None:
            cls._donation_repo = MongoDonationRepository()
            logger.info("Created MongoDB donation repository")
        return cls._donation_repo
    
    @classmethod
    def get_comment_repository(cls) -> ICommentRepository:
        """Get comment repository instance."""
        if cls._comment_repo is None:
            cls._comment_repo = MongoCommentRepository()
            logger.info("Created MongoDB comment repository")
        return cls._comment_repo
    
    @classmethod
    def get_notification_repository(cls) -> INotificationRepository:
        """Get notification repository instance."""
        if cls._notification_repo is None:
            cls._notification_repo = MongoNotificationRepository()
            logger.info("Created MongoDB notification repository")
        return cls._notification_repo
    
    @classmethod
    def get_chat_repository(cls) -> IChatRepository:
        """Get chat repository instance."""
        if cls._chat_repo is None:
            cls._chat_repo = MongoChatRepository()
            logger.info("Created MongoDB chat repository")
        return cls._chat_repo
    
    @classmethod
    def reset_repositories(cls):
        """Reset all repository instances (useful for testing)."""
        cls._user_repo = None
        cls._request_repo = None
        cls._donation_repo = None
        cls._comment_repo = None
        cls._notification_repo = None
        cls._chat_repo = None
        logger.info("Reset all repository instances")


# Convenience functions for dependency injection
def get_user_repository() -> IUserRepository:
    """Get user repository for dependency injection."""
    return RepositoryFactory.get_user_repository()


def get_request_repository() -> IRequestRepository:
    """Get request repository for dependency injection."""
    return RepositoryFactory.get_request_repository()


def get_donation_repository() -> IDonationRepository:
    """Get donation repository for dependency injection."""
    return RepositoryFactory.get_donation_repository()


def get_comment_repository() -> ICommentRepository:
    """Get comment repository for dependency injection."""
    return RepositoryFactory.get_comment_repository()


def get_notification_repository() -> INotificationRepository:
    """Get notification repository for dependency injection."""
    return RepositoryFactory.get_notification_repository()


def get_chat_repository() -> IChatRepository:
    """Get chat repository for dependency injection."""
    return RepositoryFactory.get_chat_repository()
