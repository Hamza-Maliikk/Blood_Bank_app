from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, verify_token, create_password_reset_token,
    verify_password_reset_token
)
from app.repositories.factory import get_user_repository
from app.domain.entities import UserProfile
from app.core.config import settings
from app.services.email_service import EmailService
import logging
import uuid
import secrets
import string

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for user management."""
    
    def __init__(self):
        self.user_repo = get_user_repository()
        self.email_service = EmailService()
    
    async def register_user(
        self,
        email: str,
        password: str,
        name: str,
        **profile_data
    ) -> Dict[str, Any]:
        """Register a new user."""
        try:
            # Check if user already exists
            existing_user = await self.user_repo.get_user_by_email(email)
            if existing_user:
                raise ValueError("User with this email already exists")
            
            # Generate UID (for compatibility with frontend)
            uid = str(uuid.uuid4())
            
            # Hash password
            password_hash = get_password_hash(password)
            
            # Create user profile
            user_profile = UserProfile(
                uid=uid,
                name=name,
                email=email,
                gender=profile_data.get("gender"),
                bloodGroup=profile_data.get("bloodGroup"),
                city=profile_data.get("city"),
                cnic=profile_data.get("cnic"),
                phone=profile_data.get("phone"),
                available=profile_data.get("available", True),
                mode=profile_data.get("mode", "patient"),
                role=profile_data.get("role", "user"),
                themePreference=profile_data.get("themePreference", "system")
            )
            
            # Save user to database
            created_user = await self.user_repo.create_user(user_profile, password_hash)
            
            # Generate tokens
            access_token = create_access_token({"sub": uid, "email": email})
            refresh_token = create_refresh_token({"sub": uid, "email": email})
            
            logger.info(f"User registered successfully: {uid}")
            
            return {
                "user": created_user,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise
    
    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login user with email and password."""
        try:
            # Get user by email
            user = await self.user_repo.get_user_by_email(email)
            if not user:
                raise ValueError("Invalid email or password")
            
            # Get password hash
            password_hash = await self.user_repo.get_password_hash(user.uid)
            if not password_hash:
                raise ValueError("Invalid email or password")
            
            # Verify password
            if not verify_password(password, password_hash):
                raise ValueError("Invalid email or password")
            
            # Generate tokens
            access_token = create_access_token({"sub": user.uid, "email": user.email})
            refresh_token = create_refresh_token({"sub": user.uid, "email": user.email})
            
            logger.info(f"User logged in successfully: {user.uid}")
            
            return {
                "user": user,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
            
        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            raise
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Refresh access token using refresh token."""
        try:
            # Verify refresh token
            payload = verify_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")
            
            user_id = payload.get("sub")
            email = payload.get("email")
            
            # Verify user still exists
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Generate new access token
            access_token = create_access_token({"sub": user_id, "email": email})
            
            logger.info(f"Token refreshed successfully for user: {user_id}")
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise
    
    async def request_password_reset(self, email: str) -> bool:
        """Request password reset for user."""
        try:
            # Check if user exists
            user = await self.user_repo.get_user_by_email(email)
            if not user:
                # Don't reveal if user exists or not for security
                logger.info(f"Password reset requested for email: {email}")
                return True
            
            # Generate new random password
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            new_password = ''.join(secrets.choice(alphabet) for i in range(12))
            
            # Hash new password
            password_hash = get_password_hash(new_password)
            
            # Update user's password
            await self.user_repo.update_user(user.uid, {"password_hash": password_hash})
            
            # Send email with new password
            email_sent = await self.email_service.send_password_reset_email(email, new_password)
            
            if email_sent:
                logger.info(f"Password reset and new password sent for {email}")
            else:
                logger.warning(f"Password reset email failed to send for {email}, but password was reset")
            
            return True
            
        except Exception as e:
            logger.error(f"Error requesting password reset: {e}")
            raise
    
    async def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """Confirm password reset with token."""
        try:
            # Verify reset token
            email = verify_password_reset_token(token)
            
            # Get user
            user = await self.user_repo.get_user_by_email(email)
            if not user:
                raise ValueError("User not found")
            
            # Hash new password
            password_hash = get_password_hash(new_password)
            
            # Update password
            await self.user_repo.update_user(user.uid, {"password_hash": password_hash})
            
            logger.info(f"Password reset successfully for user: {user.uid}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error confirming password reset: {e}")
            raise
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password."""
        try:
            # Get current password hash
            password_hash = await self.user_repo.get_password_hash(user_id)
            if not password_hash:
                raise ValueError("User not found")
            
            # Verify current password
            if not verify_password(current_password, password_hash):
                raise ValueError("Current password is incorrect")
            
            # Hash new password
            new_password_hash = get_password_hash(new_password)
            
            # Update password
            await self.user_repo.update_user(user_id, {"password_hash": new_password_hash})
            
            logger.info(f"Password changed successfully for user: {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            raise
    
    async def complete_onboarding(self, user_id: str, profile_data: Dict[str, Any]) -> UserProfile:
        """Complete user onboarding with profile data."""
        try:
            # Update user profile
            updated_user = await self.user_repo.update_user(user_id, profile_data)
            if not updated_user:
                raise ValueError("User not found")
            
            logger.info(f"Onboarding completed for user: {user_id}")
            
            return updated_user
            
        except Exception as e:
            logger.error(f"Error completing onboarding: {e}")
            raise
