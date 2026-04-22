from typing import Optional, List, Dict, Any
from datetime import datetime
from app.repositories.factory import get_request_repository, get_donation_repository, get_user_repository
from app.domain.entities import BloodRequest, Donation
from app.services.email_service import EmailService
from app.services.match_service import calculate_match_scores_for_request
import logging
import uuid

logger = logging.getLogger(__name__)


class RequestService:
    """Request service for blood request management."""
    
    def __init__(self):
        self.request_repo = get_request_repository()
        self.donation_repo = get_donation_repository()
        self.user_repo = get_user_repository()
        self.email_service = EmailService()
    
    async def create_blood_request(
        self,
        created_by: str,
        patient_name: str,
        required_blood_group: str,
        city: str,
        **request_data
    ) -> BloodRequest:
        """Create a new blood request."""
        try:
            # Generate request ID
            request_id = str(uuid.uuid4())
            
            # Determine initial status
            status = "pending" if request_data.get("requestedTo") else "open"
            
            # Create request
            request = BloodRequest(
                id=request_id,
                createdBy=created_by,
                patientName=patient_name,
                requiredBloodGroup=required_blood_group,
                city=city,
                gender=request_data.get("gender"),
                hospital=request_data.get("hospital"),
                locationAddress=request_data.get("locationAddress"),
                locationLat=request_data.get("locationLat"),
                locationLng=request_data.get("locationLng"),
                unitsRequired=request_data.get("unitsRequired"),
                neededBy=request_data.get("neededBy"),
                notes=request_data.get("notes"),
                requestedTo=request_data.get("requestedTo"),
                status=status
            )
            
            created_request = await self.request_repo.create_request(request)
            logger.info(f"Created blood request: {request_id}")
            
            # Send notification to targeted donor if applicable
            # if request_data.get("requestedTo"):
            #     donor_id = request_data.get("requestedTo")
            #     donor = await self.user_repo.get_user_by_id(donor_id)
            #     if donor and donor.email:
            #         try:
            #             await self.email_service.send_request_notification_to_donor(
            #                 donor_email=donor.email,
            #                 donor_name=donor.name or "Donor",
            #                 patient_name=patient_name,
            #                 blood_group=required_blood_group,
            #                 city=city,
            #                 request_id=request_id
            #             )
            #             logger.info(f"Email notification sent to targeted donor: {donor.email}")
            #         except Exception as e:
            #             logger.error(f"Failed to send email to targeted donor: {e}")
            # else:
            #     # Send notification to all matching donors (available donors with matching blood group and city)
            #     try:
            #         matching_donors = await self.user_repo.list_available_donors({
            #             "bloodGroup": required_blood_group,
            #             "city": city
            #         })
                    
            #         # Limit to first 50 donors to avoid sending too many emails
            #         for donor in matching_donors[:50]:
            #             if donor.email:
            #                 try:
            #                     await self.email_service.send_request_notification_to_donor(
            #                         donor_email=donor.email,
            #                         donor_name=donor.name or "Donor",
            #                         patient_name=patient_name,
            #                         blood_group=required_blood_group,
            #                         city=city,
            #                         request_id=request_id
            #                     )
            #                     logger.info(f"Email notification sent to matching donor: {donor.email}")
            #                 except Exception as e:
            #                     logger.error(f"Failed to send email to donor {donor.email}: {e}")
                    
            #         logger.info(f"Sent email notifications to {len(matching_donors[:50])} matching donors")
            #     except Exception as e:
            #         logger.error(f"Error sending notifications to matching donors: {e}")
            
            return created_request
            
        except Exception as e:
            logger.error(f"Error creating blood request: {e}")
            raise
    
    async def get_request_by_id(self, request_id: str) -> Optional[BloodRequest]:
        """Get blood request by ID."""
        try:
            request = await self.request_repo.get_request_by_id(request_id)
            if request:
                logger.info(f"Retrieved request: {request_id}")
            return request
        except Exception as e:
            logger.error(f"Error getting request by ID: {e}")
            raise
    
    async def list_requests(self, filters: Optional[Dict[str, Any]] = None,
                           skip: int = 0, limit: int = 100,
                           include_match_scores: bool = False,
                           viewer_user_id: Optional[str] = None) -> List[BloodRequest]:
        """
        List blood requests with filters.
        Returns BloodRequest objects. Match scores are added to __dict__ if requested.
        """
        try:
            requests = await self.request_repo.list_requests(filters, skip, limit)
            logger.info(f"Found {len(requests)} requests")
            
            # If match scores are requested and viewer is a donor, calculate scores
            if include_match_scores and viewer_user_id:
                viewer = await self.user_repo.get_user_by_id(viewer_user_id)
                if viewer and viewer.mode == "donor" and viewer.available:
                    from app.services.match_service import calculate_match_score
                    for request in requests:
                        # Calculate match score for this donor and attach to request object
                        match_data = await calculate_match_score(viewer, request)
                        # Store match score in a way that can be serialized
                        setattr(request, 'match_score_data', match_data)
                    
                    # Sort by match score
                    requests.sort(key=lambda x: getattr(x, 'match_score_data', {}).get('matchScore', 0), reverse=True)
            
            return requests
        except Exception as e:
            logger.error(f"Error listing requests: {e}")
            raise
    
    async def list_user_requests(self, user_id: str) -> List[BloodRequest]:
        """List requests created by user."""
        try:
            requests = await self.request_repo.list_user_requests(user_id)
            logger.info(f"Found {len(requests)} requests for user {user_id}")
            return requests
        except Exception as e:
            logger.error(f"Error listing user requests: {e}")
            raise
    
    async def accept_request(self, request_id: str, donor_id: str) -> Optional[BloodRequest]:
        """Accept a blood request (donor action)."""
        try:
            # Get the request
            request = await self.request_repo.get_request_by_id(request_id)
            if not request:
                raise ValueError("Request not found")
            
            # Check if request can be accepted
            if request.status not in ["open", "pending"]:
                raise ValueError("Request cannot be accepted")
            
            # If it's a targeted request, check if donor is the target
            if request.requestedTo and request.requestedTo != donor_id:
                raise ValueError("You are not the targeted donor for this request")
            
            # Update request status
            update_data = {
                "status": "accepted",
                "requestedTo": donor_id
            }
            
            updated_request = await self.request_repo.update_request(request_id, update_data)
            
            if updated_request:
                # Automatically create donation record
                donation_id = str(uuid.uuid4())
                donation = Donation(
                    id=donation_id,
                    userId=donor_id,
                    requestId=request_id,
                    status="pending"
                )
                
                await self.donation_repo.create_donation(donation)
                
                logger.info(f"Request {request_id} accepted by donor {donor_id}")
                
                # Send notification to requester
                # requester = await self.user_repo.get_user_by_id(request.createdBy)
                # donor = await self.user_repo.get_user_by_id(donor_id)
                
                # if requester and requester.email and donor:
                #     try:
                #         await self.email_service.send_request_accepted_notification(
                #             requester_email=requester.email,
                #             requester_name=requester.name or "User",
                #             donor_name=donor.name or "Donor",
                #             request_id=request_id
                #         )
                #         logger.info(f"Email notification sent to requester: {requester.email}")
                #     except Exception as e:
                #         logger.error(f"Failed to send acceptance notification email: {e}")
            
            return updated_request
            
        except Exception as e:
            logger.error(f"Error accepting request: {e}")
            raise
    
    async def reject_request(self, request_id: str, donor_id: str) -> Optional[BloodRequest]:
        """Reject a blood request (donor action)."""
        try:
            # Get the request
            request = await self.request_repo.get_request_by_id(request_id)
            if not request:
                raise ValueError("Request not found")
            
            # Check if request can be rejected
            if request.status != "pending":
                raise ValueError("Request cannot be rejected")
            
            # Check if donor is the target
            if request.requestedTo != donor_id:
                raise ValueError("You are not the targeted donor for this request")
            
            # Update request status
            update_data = {
                "status": "rejected",
                "requestedTo": donor_id
            }
            
            updated_request = await self.request_repo.update_request(request_id, update_data)
            
            if updated_request:
                logger.info(f"Request {request_id} rejected by donor {donor_id}")
            
            return updated_request
            
        except Exception as e:
            logger.error(f"Error rejecting request: {e}")
            raise
    
    async def cancel_request(self, request_id: str, creator_id: str) -> Optional[BloodRequest]:
        """Cancel a blood request (creator action)."""
        try:
            # Get the request
            request = await self.request_repo.get_request_by_id(request_id)
            if not request:
                raise ValueError("Request not found")
            
            # Check if user is the creator
            if request.createdBy != creator_id:
                raise ValueError("Only the creator can cancel this request")
            
            # Check if request can be cancelled
            if request.status in ["fulfilled", "cancelled"]:
                raise ValueError("Request cannot be cancelled")
            
            # Update request status
            update_data = {"status": "cancelled"}
            updated_request = await self.request_repo.update_request(request_id, update_data)
            
            if updated_request:
                logger.info(f"Request {request_id} cancelled by creator {creator_id}")
            
            return updated_request
            
        except Exception as e:
            logger.error(f"Error cancelling request: {e}")
            raise
    
    async def mark_request_fulfilled(self, request_id: str, creator_id: str) -> Optional[BloodRequest]:
        """Mark a blood request as fulfilled (creator action)."""
        try:
            # Get the request
            request = await self.request_repo.get_request_by_id(request_id)
            if not request:
                raise ValueError("Request not found")
            
            # Check if user is the creator
            if request.createdBy != creator_id:
                raise ValueError("Only the creator can mark this request as fulfilled")
            
            # Check if request can be fulfilled
            if request.status != "accepted":
                raise ValueError("Request must be accepted before it can be fulfilled")
            
            # Update request status
            update_data = {"status": "fulfilled"}
            updated_request = await self.request_repo.update_request(request_id, update_data)
            
            if updated_request:
                # Update donation status
                donations = await self.donation_repo.list_user_donations(request.requestedTo)
                for donation in donations:
                    if donation.requestId == request_id:
                        await self.donation_repo.update_donation(
                            donation.id, 
                            {"status": "donated"}
                        )
                        break
                
                logger.info(f"Request {request_id} marked as fulfilled by creator {creator_id}")
            
            return updated_request
            
        except Exception as e:
            logger.error(f"Error marking request as fulfilled: {e}")
            raise
    
    async def get_donor_inbox(self, donor_id: str) -> Dict[str, List[BloodRequest]]:
        """Get donor inbox (targeted + discoverable requests)."""
        try:
            inbox = await self.request_repo.list_donor_inbox(donor_id)
            logger.info(f"Retrieved inbox for donor {donor_id}")
            return inbox
        except Exception as e:
            logger.error(f"Error getting donor inbox: {e}")
            raise
    
    async def get_donor_statistics(self, donor_id: str) -> Dict[str, int]:
        """Get donor statistics."""
        try:
            stats = await self.request_repo.get_donor_stats(donor_id)
            logger.info(f"Retrieved statistics for donor {donor_id}")
            return stats
        except Exception as e:
            logger.error(f"Error getting donor statistics: {e}")
            raise
