from typing import Optional, List, Dict, Any
from datetime import datetime
from app.repositories.factory import get_donation_repository
from app.domain.entities import Donation, MoneyDonation
import logging
import uuid
import stripe
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class DonationService:
    """Donation service for blood and money donation management."""
    
    def __init__(self):
        self.donation_repo = get_donation_repository()
    
    # Blood Donations
    async def get_blood_donation_by_id(self, donation_id: str) -> Optional[Donation]:
        """Get blood donation by ID."""
        try:
            donation = await self.donation_repo.get_donation_by_id(donation_id)
            if donation:
                logger.info(f"Retrieved blood donation: {donation_id}")
            return donation
        except Exception as e:
            logger.error(f"Error getting blood donation by ID: {e}")
            raise
    
    async def update_blood_donation_status(self, donation_id: str, status: str) -> Optional[Donation]:
        """Update blood donation status."""
        try:
            if status not in ["pending", "donated", "cancelled"]:
                raise ValueError("Invalid donation status")
            
            updated_donation = await self.donation_repo.update_donation(
                donation_id, 
                {"status": status}
            )
            
            if updated_donation:
                logger.info(f"Updated blood donation {donation_id} status to {status}")
            
            return updated_donation
        except Exception as e:
            logger.error(f"Error updating blood donation status: {e}")
            raise
    
    async def list_user_blood_donations(self, user_id: str) -> List[Donation]:
        """List user's blood donations."""
        try:
            donations = await self.donation_repo.list_user_donations(user_id)
            logger.info(f"Found {len(donations)} blood donations for user {user_id}")
            return donations
        except Exception as e:
            logger.error(f"Error listing user blood donations: {e}")
            raise
    
    # Money Donations
    async def create_payment_intent(
        self,
        user_id: str,
        amount: float,
        currency: str = "PKR",
        purpose: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create Stripe payment intent for money donation."""
        try:
            # Convert PKR to cents (Stripe uses smallest currency unit)
            amount_in_cents = int(amount * 100)
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency=currency.lower(),
                metadata={
                    "user_id": user_id,
                    "purpose": purpose or "General Donation"
                }
            )
            
            logger.info(f"Created payment intent for user {user_id}: {intent.id}")
            
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": amount,
                "currency": currency
            }
            
        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            raise
    
    async def confirm_money_donation(
        self,
        user_id: str,
        payment_intent_id: str,
        amount: float,
        currency: str = "PKR",
        purpose: Optional[str] = None
    ) -> MoneyDonation:
        """Confirm money donation after successful payment."""
        try:
            # Retrieve payment intent from Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Check if payment was successful
            if intent.status != "succeeded":
                raise ValueError("Payment was not successful")
            
            # Check if donation already exists
            existing_donation = await self.donation_repo.get_money_donation_by_stripe_id(payment_intent_id)
            if existing_donation:
                logger.warning(f"Donation already exists for payment intent: {payment_intent_id}")
                return existing_donation
            
            # Create donation record
            donation_id = str(uuid.uuid4())
            donation = MoneyDonation(
                id=donation_id,
                uid=user_id,
                amount=amount,
                currency=currency,
                purpose=purpose,
                stripePaymentId=payment_intent_id,
                stripeSessionId=intent.get("latest_charge"),
                receiptUrl=f"https://dashboard.stripe.com/payments/{payment_intent_id}"
            )
            
            created_donation = await self.donation_repo.create_money_donation(donation)
            
            logger.info(f"Confirmed money donation: {donation_id}")
            return created_donation
            
        except Exception as e:
            logger.error(f"Error confirming money donation: {e}")
            raise
    
    async def get_money_donation_by_id(self, donation_id: str) -> Optional[MoneyDonation]:
        """Get money donation by ID."""
        try:
            donation = await self.donation_repo.get_money_donation_by_id(donation_id)
            if donation:
                logger.info(f"Retrieved money donation: {donation_id}")
            return donation
        except Exception as e:
            logger.error(f"Error getting money donation by ID: {e}")
            raise
    
    async def list_user_money_donations(self, user_id: str) -> List[MoneyDonation]:
        """List user's money donations."""
        try:
            donations = await self.donation_repo.list_user_money_donations(user_id)
            logger.info(f"Found {len(donations)} money donations for user {user_id}")
            return donations
        except Exception as e:
            logger.error(f"Error listing user money donations: {e}")
            raise
    
    async def list_money_donations(self, skip: int = 0, limit: int = 100) -> List[MoneyDonation]:
        """List all money donations with pagination."""
        try:
            donations = await self.donation_repo.list_money_donations(skip, limit)
            logger.info(f"Retrieved {len(donations)} money donations")
            return donations
        except Exception as e:
            logger.error(f"Error listing money donations: {e}")
            raise
    
    async def get_donation_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user's donation statistics."""
        try:
            # Get blood donations
            blood_donations = await self.donation_repo.list_user_donations(user_id)
            
            # Get money donations
            money_donations = await self.donation_repo.list_user_money_donations(user_id)
            
            # Calculate statistics
            stats = {
                "blood_donations": {
                    "total": len(blood_donations),
                    "completed": len([d for d in blood_donations if d.status == "donated"]),
                    "pending": len([d for d in blood_donations if d.status == "pending"]),
                    "cancelled": len([d for d in blood_donations if d.status == "cancelled"])
                },
                "money_donations": {
                    "total": len(money_donations),
                    "total_amount": sum(d.amount for d in money_donations),
                    "currency": "PKR"
                }
            }
            
            logger.info(f"Retrieved donation statistics for user {user_id}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting donation statistics: {e}")
            raise
    
    async def process_stripe_webhook(self, event_data: Dict[str, Any]) -> bool:
        """Process Stripe webhook events."""
        try:
            event_type = event_data.get("type")
            
            if event_type == "payment_intent.succeeded":
                payment_intent = event_data.get("data", {}).get("object", {})
                payment_intent_id = payment_intent.get("id")
                
                # Check if we already have this donation
                existing_donation = await self.donation_repo.get_money_donation_by_stripe_id(payment_intent_id)
                if existing_donation:
                    logger.info(f"Donation already processed for payment intent: {payment_intent_id}")
                    return True
                
                # Create donation record
                metadata = payment_intent.get("metadata", {})
                user_id = metadata.get("user_id")
                purpose = metadata.get("purpose")
                amount = payment_intent.get("amount", 0) / 100  # Convert from cents
                currency = payment_intent.get("currency", "PKR").upper()
                
                if user_id:
                    donation_id = str(uuid.uuid4())
                    donation = MoneyDonation(
                        id=donation_id,
                        uid=user_id,
                        amount=amount,
                        currency=currency,
                        purpose=purpose,
                        stripePaymentId=payment_intent_id,
                        stripeSessionId=payment_intent.get("latest_charge"),
                        receiptUrl=f"https://dashboard.stripe.com/payments/{payment_intent_id}"
                    )
                    
                    await self.donation_repo.create_money_donation(donation)
                    logger.info(f"Processed webhook donation: {donation_id}")
                
            return True
            
        except Exception as e:
            logger.error(f"Error processing Stripe webhook: {e}")
            raise
