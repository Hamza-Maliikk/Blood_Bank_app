from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.services.request_service import RequestService
from app.core.security import get_current_user, get_current_user_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
request_service = RequestService()


# Request/Response Models
class BloodRequestCreate(BaseModel):
    patientName: str
    requiredBloodGroup: str
    city: str
    gender: Optional[str] = None
    hospital: Optional[str] = None
    locationAddress: Optional[str] = None
    locationLat: Optional[float] = None
    locationLng: Optional[float] = None
    unitsRequired: Optional[int] = None
    neededBy: Optional[datetime] = None
    notes: Optional[str] = None
    requestedTo: Optional[str] = None


@router.post("/")
async def create_blood_request(
    request_data: BloodRequestCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new blood request."""
    try:
        user_id = current_user["user_id"]
        
        request = await request_service.create_blood_request(
            created_by=user_id,
            patient_name=request_data.patientName,
            required_blood_group=request_data.requiredBloodGroup,
            city=request_data.city,
            gender=request_data.gender,
            hospital=request_data.hospital,
            locationAddress=request_data.locationAddress,
            locationLat=request_data.locationLat,
            locationLng=request_data.locationLng,
            unitsRequired=request_data.unitsRequired,
            neededBy=request_data.neededBy,
            notes=request_data.notes,
            requestedTo=request_data.requestedTo
        )
        
        return {
            "success": True,
            "data": request.__dict__,
            "message": "Blood request created successfully"
        }
        
    except Exception as e:
        logger.error(f"Create blood request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create blood request"
        )


@router.get("/")
async def list_requests(
    status: Optional[str] = Query(None, description="Filter by status"),
    city: Optional[str] = Query(None, description="Filter by city"),
    requiredBloodGroup: Optional[str] = Query(None, description="Filter by blood group"),
    mineOnly: bool = Query(False, description="Show only my requests"),
    toMeOnly: bool = Query(False, description="Show only requests to me"),
    openOnly: bool = Query(False, description="Show only open requests"),
    includeMatchScores: bool = Query(False, description="Include match scores for current user"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """List blood requests with filters. Can include match scores if user is a donor."""
    try:
        user_id = current_user["user_id"]
        
        filters = {}
        if status:
            filters["status"] = status
        if city:
            filters["city"] = city
        if requiredBloodGroup:
            filters["requiredBloodGroup"] = requiredBloodGroup
        if mineOnly:
            filters["mineOnly"] = True
            filters["user_id"] = user_id
        if toMeOnly:
            filters["toMeOnly"] = True
            filters["user_id"] = user_id
        if openOnly:
            filters["openOnly"] = True
        
        requests = await request_service.list_requests(
            filters, skip, limit,
            include_match_scores=includeMatchScores,
            viewer_user_id=user_id if includeMatchScores else None
        )
        
        # Convert to dictionaries and include match scores if present
        request_dicts = []
        for req in requests:
            req_dict = req.__dict__.copy()
            # Include match score data if present
            if hasattr(req, 'match_score_data'):
                req_dict['matchScore'] = req.match_score_data
            request_dicts.append(req_dict)
        
        return {
            "success": True,
            "data": request_dicts,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "count": len(request_dicts)
            }
        }
        
    except Exception as e:
        logger.error(f"List requests error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list requests"
        )


@router.get("/inbox")
async def get_donor_inbox(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get donor inbox (targeted + discoverable requests)."""
    try:
        user_id = current_user["user_id"]
        
        inbox = await request_service.get_donor_inbox(user_id)
        
        return {
            "success": True,
            "data": {
                "targeted": [req.__dict__ for req in inbox["targeted"]],
                "discoverable": [req.__dict__ for req in inbox["discoverable"]]
            }
        }
        
    except Exception as e:
        logger.error(f"Get donor inbox error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get donor inbox"
        )


@router.get("/{request_id}")
async def get_request_by_id(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get specific blood request."""
    try:
        request = await request_service.get_request_by_id(request_id)
        
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        
        return {
            "success": True,
            "data": request.__dict__
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get request by ID error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get request"
        )


@router.put("/{request_id}/accept")
async def accept_request(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Accept a blood request (donor action)."""
    try:
        user_id = current_user["user_id"]
        
        updated_request = await request_service.accept_request(request_id, user_id)
        
        if not updated_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        
        return {
            "success": True,
            "data": updated_request.__dict__,
            "message": "Request accepted successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Accept request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept request"
        )


@router.put("/{request_id}/reject")
async def reject_request(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Reject a blood request (donor action)."""
    try:
        user_id = current_user["user_id"]
        
        updated_request = await request_service.reject_request(request_id, user_id)
        
        if not updated_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        
        return {
            "success": True,
            "data": updated_request.__dict__,
            "message": "Request rejected"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reject request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject request"
        )


@router.put("/{request_id}/cancel")
async def cancel_request(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Cancel a blood request (creator action)."""
    try:
        user_id = current_user["user_id"]
        
        updated_request = await request_service.cancel_request(request_id, user_id)
        
        if not updated_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        
        return {
            "success": True,
            "data": updated_request.__dict__,
            "message": "Request cancelled"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancel request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel request"
        )


@router.put("/{request_id}/fulfill")
async def mark_request_fulfilled(
    request_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Mark a blood request as fulfilled (creator action)."""
    try:
        user_id = current_user["user_id"]
        
        updated_request = await request_service.mark_request_fulfilled(request_id, user_id)
        
        if not updated_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        
        return {
            "success": True,
            "data": updated_request.__dict__,
            "message": "Request marked as fulfilled"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mark request fulfilled error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark request as fulfilled"
        )
