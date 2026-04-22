from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.donation_service import DonationService
from app.core.security import get_current_user, get_current_user_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
donation_service = DonationService()


# Request/Response Models
class PaymentIntentCreate(BaseModel):
    amount: float
    currency: str = "PKR"
    purpose: Optional[str] = None


class PaymentConfirm(BaseModel):
    payment_intent_id: str
    amount: float
    currency: str = "PKR"
    purpose: Optional[str] = None


class DonationStatusUpdate(BaseModel):
    status: str


@router.get("/blood")
async def list_blood_donations(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List user's blood donations."""
    try:
        user_id = current_user["user_id"]
        donations = await donation_service.list_user_blood_donations(user_id)
        
        return {
            "success": True,
            "data": [donation.__dict__ for donation in donations]
        }
        
    except Exception as e:
        logger.error(f"List blood donations error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list blood donations"
        )


@router.put("/blood/{donation_id}")
async def update_blood_donation_status(
    donation_id: str,
    status_data: DonationStatusUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update blood donation status."""
    try:
        updated_donation = await donation_service.update_blood_donation_status(
            donation_id, status_data.status
        )
        
        if not updated_donation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Donation not found"
            )
        
        return {
            "success": True,
            "data": updated_donation.__dict__,
            "message": "Donation status updated"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update donation status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update donation status"
        )


@router.post("/money/intent")
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create Stripe payment intent for money donation."""
    try:
        user_id = current_user["user_id"]
        
        result = await donation_service.create_payment_intent(
            user_id=user_id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            purpose=payment_data.purpose
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Create payment intent error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment intent"
        )


@router.post("/money/confirm")
async def confirm_money_donation(
    payment_data: PaymentConfirm,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Confirm money donation after successful payment."""
    try:
        user_id = current_user["user_id"]
        
        donation = await donation_service.confirm_money_donation(
            user_id=user_id,
            payment_intent_id=payment_data.payment_intent_id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            purpose=payment_data.purpose
        )
        
        return {
            "success": True,
            "data": donation.__dict__,
            "message": "Money donation confirmed"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Confirm money donation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm money donation"
        )


@router.get("/money")
async def list_money_donations(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List user's money donations."""
    try:
        user_id = current_user["user_id"]
        donations = await donation_service.list_user_money_donations(user_id)
        
        return {
            "success": True,
            "data": [donation.__dict__ for donation in donations]
        }
        
    except Exception as e:
        logger.error(f"List money donations error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list money donations"
        )


@router.get("/stats")
async def get_donation_statistics(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's donation statistics."""
    try:
        user_id = current_user["user_id"]
        stats = await donation_service.get_donation_statistics(user_id)
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Get donation statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get donation statistics"
        )
