from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.user_service import UserService
from app.core.security import get_current_user, get_current_user_id, require_admin
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
user_service = UserService()


# Request/Response Models
class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    bloodGroup: Optional[str] = None
    city: Optional[str] = None
    cnic: Optional[str] = None
    phone: Optional[str] = None
    mode: Optional[str] = None
    themePreference: Optional[str] = None
    locationLat: Optional[float] = None
    locationLng: Optional[float] = None


class AvailabilityToggle(BaseModel):
    available: bool


class ModeSwitch(BaseModel):
    mode: str


class UserRoleUpdate(BaseModel):
    role: str


@router.get("/profile")
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user profile."""
    try:
        user_id = current_user["user_id"]
        profile = await user_service.get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return {
            "success": True,
            "data": profile.__dict__
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@router.get("/donors")
async def list_available_donors(
    bloodGroup: Optional[str] = Query(None, description="Filter by blood group"),
    city: Optional[str] = Query(None, description="Filter by city"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return")
):
    """List available donors with optional filters."""
    try:
        filters = {}
        if bloodGroup:
            filters["bloodGroup"] = bloodGroup
        if city:
            filters["city"] = city
        if gender:
            filters["gender"] = gender
        
        donors = await user_service.list_available_donors(filters)
        
        # Apply pagination
        total = len(donors)
        paginated_donors = donors[skip:skip + limit]
        
        return {
            "success": True,
            "data": [donor.__dict__ for donor in paginated_donors],
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": skip + limit < total
            }
        }
        
    except Exception as e:
        logger.error(f"List available donors error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list available donors"
        )


@router.get("/stats")
async def get_user_statistics(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user statistics."""
    try:
        user_id = current_user["user_id"]
        stats = await user_service.get_user_statistics(user_id)
        
        return {
            "success": True,
            "data": stats
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Get user statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user statistics"
        )


@router.get("/{user_id}")
async def get_user_by_id(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user profile by ID (public info only)."""
    try:
        profile = await user_service.get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Return only public information (no email, password, etc.)
        public_data = {
            "uid": profile.uid,
            "name": profile.name,
            "bloodGroup": profile.bloodGroup,
            "city": profile.city,
            "gender": profile.gender,
            "mode": profile.mode,
            "available": profile.available if profile.mode == "donor" else None
        }
        
        return {
            "success": True,
            "data": public_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user by ID error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )


@router.put("/profile")
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user profile."""
    try:
        user_id = current_user["user_id"]
        
        # Convert to dict and remove None values
        update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
        
        updated_profile = await user_service.update_user_profile(user_id, update_data)
        
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return {
            "success": True,
            "data": updated_profile.__dict__,
            "message": "Profile updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


@router.put("/availability")
async def toggle_donor_availability(
    availability_data: AvailabilityToggle,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Toggle donor availability."""
    try:
        user_id = current_user["user_id"]
        
        success = await user_service.toggle_donor_availability(
            user_id, availability_data.available
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update availability"
            )
        
        return {
            "success": True,
            "message": f"Availability set to {availability_data.available}",
            "available": availability_data.available
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Toggle availability error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update availability"
        )


@router.put("/mode")
async def switch_user_mode(
    mode_data: ModeSwitch,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Switch user between donor and patient mode."""
    try:
        user_id = current_user["user_id"]
        
        updated_profile = await user_service.switch_user_mode(user_id, mode_data.mode)
        
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return {
            "success": True,
            "data": updated_profile.__dict__,
            "message": f"Mode switched to {mode_data.mode}"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Switch mode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to switch mode"
        )


# Admin endpoints
@router.get("/all")
async def list_all_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    admin_user: Dict[str, Any] = Depends(require_admin)
):
    """List all users (admin only)."""
    try:
        users = await user_service.list_all_users(skip, limit)
        
        return {
            "success": True,
            "data": [user.__dict__ for user in users],
            "pagination": {
                "skip": skip,
                "limit": limit,
                "count": len(users)
            }
        }
        
    except Exception as e:
        logger.error(f"List all users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )


@router.put("/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_data: UserRoleUpdate,
    admin_user: Dict[str, Any] = Depends(require_admin)
):
    """Update user role (admin only)."""
    try:
        updated_user = await user_service.update_user_role(user_id, role_data.role)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "success": True,
            "data": updated_user.__dict__,
            "message": f"User role updated to {role_data.role}"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user role error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )
