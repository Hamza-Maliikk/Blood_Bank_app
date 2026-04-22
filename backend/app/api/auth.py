from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from app.services.auth_service import AuthService
from app.core.security import get_current_user, get_current_user_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
auth_service = AuthService()


# Request/Response Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    gender: Optional[str] = None
    bloodGroup: Optional[str] = None
    city: Optional[str] = None
    cnic: Optional[str] = None
    phone: Optional[str] = None
    mode: str = "patient"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: Dict[str, Any]


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class OnboardingComplete(BaseModel):
    name: str
    gender: str
    bloodGroup: str
    city: str
    phone: str
    cnic: Optional[str] = None
    mode: str = "patient"
    available: bool = True


@router.post("/register", response_model=TokenResponse)
async def register_user(user_data: UserRegister):
    """Register a new user."""
    try:
        result = await auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
            gender=user_data.gender,
            bloodGroup=user_data.bloodGroup,
            city=user_data.city,
            cnic=user_data.cnic,
            phone=user_data.phone,
            mode=user_data.mode
        )
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            user=result["user"].__dict__
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """Login user with email and password."""
    try:
        result = await auth_service.login_user(
            email=login_data.email,
            password=login_data.password
        )
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            user=result["user"].__dict__
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    try:
        result = await auth_service.refresh_token(request.refresh_token)
        
        return {
            "access_token": result["access_token"],
            "token_type": result["token_type"]
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/reset-password")
async def request_password_reset(request: PasswordResetRequest):
    """Request password reset."""
    try:
        await auth_service.request_password_reset(request.email)
        
        return {
            "message": "Password reset email sent",
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        # Don't reveal if email exists or not
        return {
            "message": "Password reset email sent",
            "success": True
        }


@router.post("/confirm-reset")
async def confirm_password_reset(request: PasswordResetConfirm):
    """Confirm password reset with token."""
    try:
        await auth_service.confirm_password_reset(
            token=request.token,
            new_password=request.new_password
        )
        
        return {
            "message": "Password reset successfully",
            "success": True
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Password reset confirmation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.post("/change-password")
async def change_password(
    request: PasswordChange,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Change user password."""
    try:
        user_id = current_user["user_id"]
        
        await auth_service.change_password(
            user_id=user_id,
            current_password=request.current_password,
            new_password=request.new_password
        )
        
        return {
            "message": "Password changed successfully",
            "success": True
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.post("/complete-onboarding")
async def complete_onboarding(
    onboarding_data: OnboardingComplete,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Complete user onboarding."""
    try:
        user_id = current_user["user_id"]
        
        profile_data = {
            "name": onboarding_data.name,
            "gender": onboarding_data.gender,
            "bloodGroup": onboarding_data.bloodGroup,
            "city": onboarding_data.city,
            "phone": onboarding_data.phone,
            "cnic": onboarding_data.cnic,
            "mode": onboarding_data.mode,
            "available": onboarding_data.available
        }
        
        updated_user = await auth_service.complete_onboarding(user_id, profile_data)
        
        return {
            "message": "Onboarding completed successfully",
            "user": updated_user.__dict__,
            "success": True
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Onboarding completion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Onboarding completion failed"
        )


@router.get("/me")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information."""
    try:
        from app.services.user_service import UserService
        user_service = UserService()
        user = await user_service.get_user_profile(current_user["user_id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return {
            "success": True,
            "data": user.__dict__
        }
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )
