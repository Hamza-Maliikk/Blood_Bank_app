from typing import Optional, List, Dict, Any
from app.repositories.factory import get_user_repository, get_request_repository
from app.domain.entities import UserProfile
import logging

logger = logging.getLogger(__name__)


class UserService:
    """User service for profile management and donor operations."""
    
    def __init__(self):
        self.user_repo = get_user_repository()
        self.request_repo = get_request_repository()
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID."""
        try:
            user = await self.user_repo.get_user_by_id(user_id)
            if user:
                logger.info(f"Retrieved profile for user: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            raise
    
    async def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> Optional[UserProfile]:
        """Update user profile."""
        try:
            # Remove sensitive fields that shouldn't be updated directly
            sensitive_fields = ["password_hash", "role", "createdAt"]
            for field in sensitive_fields:
                update_data.pop(field, None)
            
            updated_user = await self.user_repo.update_user(user_id, update_data)
            if updated_user:
                logger.info(f"Updated profile for user: {user_id}")
            return updated_user
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            raise
    
    async def list_available_donors(self, filters: Optional[Dict[str, Any]] = None) -> List[UserProfile]:
        """List available donors with optional filters."""
        try:
            donors = await self.user_repo.list_available_donors(filters)
            logger.info(f"Found {len(donors)} available donors")
            return donors
        except Exception as e:
            logger.error(f"Error listing available donors: {e}")
            raise
    
    async def toggle_donor_availability(self, user_id: str, available: bool) -> bool:
        """Toggle donor availability."""
        try:
            # First check if user exists and is a donor
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            if user.mode != "donor":
                raise ValueError("User is not in donor mode")
            
            success = await self.user_repo.update_availability(user_id, available)
            if success:
                logger.info(f"Updated availability for user {user_id}: {available}")
            return success
        except Exception as e:
            logger.error(f"Error toggling donor availability: {e}")
            raise
    
    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            stats = {
                "profile_complete": self._is_profile_complete(user),
                "donor_mode": user.mode == "donor",
                "available_as_donor": user.available if user.mode == "donor" else False,
                "total_requests_created": 0,
                "total_donations_made": 0,
                "total_money_donated": 0.0
            }
            
            # Get request statistics if user is a donor
            if user.mode == "donor":
                donor_stats = await self.request_repo.get_donor_stats(user_id)
                stats.update(donor_stats)
            
            # TODO: Add donation and money donation statistics
            # This would require additional repository calls
            
            logger.info(f"Retrieved statistics for user: {user_id}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            raise
    
    async def switch_user_mode(self, user_id: str, mode: str) -> Optional[UserProfile]:
        """Switch user between donor and patient mode."""
        try:
            if mode not in ["donor", "patient"]:
                raise ValueError("Invalid mode. Must be 'donor' or 'patient'")
            
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            update_data = {"mode": mode}
            
            # If switching to patient mode, set available to False
            if mode == "patient":
                update_data["available"] = False
            
            updated_user = await self.user_repo.update_user(user_id, update_data)
            if updated_user:
                logger.info(f"Switched user {user_id} to {mode} mode")
            return updated_user
            
        except Exception as e:
            logger.error(f"Error switching user mode: {e}")
            raise
    
    async def list_all_users(self, skip: int = 0, limit: int = 100) -> List[UserProfile]:
        """List all users (admin only)."""
        try:
            users = await self.user_repo.list_all_users(skip, limit)
            logger.info(f"Retrieved {len(users)} users")
            return users
        except Exception as e:
            logger.error(f"Error listing all users: {e}")
            raise
    
    async def update_user_role(self, user_id: str, role: str) -> Optional[UserProfile]:
        """Update user role (admin only)."""
        try:
            if role not in ["user", "admin"]:
                raise ValueError("Invalid role. Must be 'user' or 'admin'")
            
            updated_user = await self.user_repo.update_user(user_id, {"role": role})
            if updated_user:
                logger.info(f"Updated role for user {user_id} to {role}")
            return updated_user
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            raise
    
    def _is_profile_complete(self, user: UserProfile) -> bool:
        """Check if user profile is complete."""
        required_fields = ["name", "email", "gender", "bloodGroup", "city", "phone"]
        return all(getattr(user, field) for field in required_fields)
