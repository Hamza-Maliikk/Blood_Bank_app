from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.repositories.base import IDonationRepository
from app.domain.entities import Donation, MoneyDonation
import logging

logger = logging.getLogger(__name__)


class MongoDonationRepository(IDonationRepository):
    """MongoDB implementation of donation repository."""
    
    def __init__(self):
        self.db = get_database()
        self.blood_donations = self.db.donations
        self.money_donations = self.db.money_donations
    
    # Blood Donations
    async def create_donation(self, donation: Donation) -> Donation:
        """Create a new blood donation."""
        try:
            donation_dict = {
                "id": donation.id,
                "userId": donation.userId,
                "requestId": donation.requestId,
                "status": donation.status,
                "date": donation.date
            }
            
            result = await self.blood_donations.insert_one(donation_dict)
            if result.inserted_id:
                logger.info(f"Blood donation created successfully: {donation.id}")
                return donation
            else:
                raise Exception("Failed to create blood donation")
                
        except Exception as e:
            logger.error(f"Error creating blood donation: {e}")
            raise
    
    async def get_donation_by_id(self, donation_id: str) -> Optional[Donation]:
        """Get donation by ID."""
        try:
            donation_doc = await self.blood_donations.find_one({"id": donation_id})
            if donation_doc:
                return self._doc_to_donation(donation_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting donation by ID: {e}")
            raise
    
    async def update_donation(self, donation_id: str, update_data: Dict[str, Any]) -> Optional[Donation]:
        """Update donation."""
        try:
            result = await self.blood_donations.update_one(
                {"id": donation_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                updated_donation = await self.get_donation_by_id(donation_id)
                logger.info(f"Donation updated successfully: {donation_id}")
                return updated_donation
            return None
            
        except Exception as e:
            logger.error(f"Error updating donation: {e}")
            raise
    
    async def list_user_donations(self, user_id: str) -> List[Donation]:
        """List user's blood donations."""
        try:
            cursor = self.blood_donations.find({"userId": user_id}).sort("date", -1)
            donations = []
            async for doc in cursor:
                donations.append(self._doc_to_donation(doc))
            
            logger.info(f"Found {len(donations)} blood donations for user {user_id}")
            return donations
            
        except Exception as e:
            logger.error(f"Error listing user donations: {e}")
            raise
    
    # Money Donations
    async def create_money_donation(self, donation: MoneyDonation) -> MoneyDonation:
        """Create a new money donation."""
        try:
            donation_dict = {
                "id": donation.id,
                "uid": donation.uid,
                "amount": donation.amount,
                "currency": donation.currency,
                "purpose": donation.purpose,
                "stripePaymentId": donation.stripePaymentId,
                "stripeSessionId": donation.stripeSessionId,
                "receiptUrl": donation.receiptUrl,
                "createdAt": donation.createdAt
            }
            
            # Remove None values
            donation_dict = {k: v for k, v in donation_dict.items() if v is not None}
            
            result = await self.money_donations.insert_one(donation_dict)
            if result.inserted_id:
                logger.info(f"Money donation created successfully: {donation.id}")
                return donation
            else:
                raise Exception("Failed to create money donation")
                
        except Exception as e:
            logger.error(f"Error creating money donation: {e}")
            raise
    
    async def get_money_donation_by_id(self, donation_id: str) -> Optional[MoneyDonation]:
        """Get money donation by ID."""
        try:
            donation_doc = await self.money_donations.find_one({"id": donation_id})
            if donation_doc:
                return self._doc_to_money_donation(donation_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting money donation by ID: {e}")
            raise
    
    async def list_user_money_donations(self, user_id: str) -> List[MoneyDonation]:
        """List user's money donations."""
        try:
            cursor = self.money_donations.find({"uid": user_id}).sort("createdAt", -1)
            donations = []
            async for doc in cursor:
                donations.append(self._doc_to_money_donation(doc))
            
            logger.info(f"Found {len(donations)} money donations for user {user_id}")
            return donations
            
        except Exception as e:
            logger.error(f"Error listing user money donations: {e}")
            raise
    
    async def get_money_donation_by_stripe_id(self, stripe_payment_id: str) -> Optional[MoneyDonation]:
        """Get money donation by Stripe payment ID."""
        try:
            donation_doc = await self.money_donations.find_one({"stripePaymentId": stripe_payment_id})
            if donation_doc:
                return self._doc_to_money_donation(donation_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting money donation by Stripe ID: {e}")
            raise
    
    async def list_money_donations(self, skip: int = 0, limit: int = 100) -> List[MoneyDonation]:
        """List all money donations with pagination."""
        try:
            cursor = self.money_donations.find().skip(skip).limit(limit)
            donations = []
            async for doc in cursor:
                donations.append(self._doc_to_money_donation(doc))
            logger.info(f"Retrieved {len(donations)} money donations")
            return donations
        except Exception as e:
            logger.error(f"Error listing money donations: {e}")
            raise
    
    def _doc_to_donation(self, doc: Dict[str, Any]) -> Donation:
        """Convert MongoDB document to Donation."""
        return Donation(
            id=doc["id"],
            userId=doc["userId"],
            requestId=doc["requestId"],
            status=doc.get("status", "pending"),
            date=doc.get("date")
        )
    
    def _doc_to_money_donation(self, doc: Dict[str, Any]) -> MoneyDonation:
        """Convert MongoDB document to MoneyDonation."""
        return MoneyDonation(
            id=doc["id"],
            uid=doc["uid"],
            amount=doc["amount"],
            currency=doc.get("currency", "PKR"),
            purpose=doc.get("purpose"),
            stripePaymentId=doc.get("stripePaymentId"),
            stripeSessionId=doc.get("stripeSessionId"),
            receiptUrl=doc.get("receiptUrl"),
            createdAt=doc.get("createdAt")
        )
