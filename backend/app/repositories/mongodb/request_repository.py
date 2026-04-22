from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.repositories.base import IRequestRepository
from app.domain.entities import BloodRequest
import logging

logger = logging.getLogger(__name__)


class MongoRequestRepository(IRequestRepository):
    """MongoDB implementation of request repository."""
    
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.requests
    
    async def create_request(self, request: BloodRequest) -> BloodRequest:
        """Create a new blood request."""
        try:
            request_dict = {
                "id": request.id,
                "createdBy": request.createdBy,
                "patientName": request.patientName,
                "requiredBloodGroup": request.requiredBloodGroup,
                "city": request.city,
                "gender": request.gender,
                "hospital": request.hospital,
                "locationAddress": request.locationAddress,
                "locationLat": request.locationLat,
                "locationLng": request.locationLng,
                "unitsRequired": request.unitsRequired,
                "neededBy": request.neededBy,
                "notes": request.notes,
                "requestedTo": request.requestedTo,
                "status": request.status,
                "createdAt": request.createdAt
            }
            
            # Remove None values
            request_dict = {k: v for k, v in request_dict.items() if v is not None}
            
            result = await self.collection.insert_one(request_dict)
            if result.inserted_id:
                logger.info(f"Request created successfully: {request.id}")
                return request
            else:
                raise Exception("Failed to create request")
                
        except Exception as e:
            logger.error(f"Error creating request: {e}")
            raise
    
    async def get_request_by_id(self, request_id: str) -> Optional[BloodRequest]:
        """Get request by ID."""
        try:
            request_doc = await self.collection.find_one({"id": request_id})
            if request_doc:
                return self._doc_to_request(request_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting request by ID: {e}")
            raise
    
    async def update_request(self, request_id: str, update_data: Dict[str, Any]) -> Optional[BloodRequest]:
        """Update request."""
        try:
            result = await self.collection.update_one(
                {"id": request_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                updated_request = await self.get_request_by_id(request_id)
                logger.info(f"Request updated successfully: {request_id}")
                return updated_request
            return None
            
        except Exception as e:
            logger.error(f"Error updating request: {e}")
            raise
    
    async def list_requests(self, filters: Optional[Dict[str, Any]] = None,
                           skip: int = 0, limit: int = 100) -> List[BloodRequest]:
        """List requests with filters."""
        try:
            query = {}
            
            if filters:
                if "status" in filters:
                    if isinstance(filters["status"], list):
                        query["status"] = {"$in": filters["status"]}
                    else:
                        query["status"] = filters["status"]
                
                if "city" in filters:
                    query["city"] = filters["city"]
                
                if "requiredBloodGroup" in filters:
                    query["requiredBloodGroup"] = filters["requiredBloodGroup"]
                
                if "createdBy" in filters:
                    query["createdBy"] = filters["createdBy"]
                
                if "requestedTo" in filters:
                    query["requestedTo"] = filters["requestedTo"]
                
                if "mineOnly" in filters and filters["mineOnly"]:
                    query["createdBy"] = filters.get("user_id")
                
                if "toMeOnly" in filters and filters["toMeOnly"]:
                    query["requestedTo"] = filters.get("user_id")
                
                if "openOnly" in filters and filters["openOnly"]:
                    query["status"] = "open"
            
            cursor = self.collection.find(query).sort("createdAt", -1).skip(skip).limit(limit)
            requests = []
            async for doc in cursor:
                requests.append(self._doc_to_request(doc))
            
            logger.info(f"Found {len(requests)} requests")
            return requests
            
        except Exception as e:
            logger.error(f"Error listing requests: {e}")
            raise
    
    async def list_user_requests(self, user_id: str) -> List[BloodRequest]:
        """List requests created by user."""
        try:
            cursor = self.collection.find({"createdBy": user_id}).sort("createdAt", -1)
            requests = []
            async for doc in cursor:
                requests.append(self._doc_to_request(doc))
            
            logger.info(f"Found {len(requests)} requests for user {user_id}")
            return requests
            
        except Exception as e:
            logger.error(f"Error listing user requests: {e}")
            raise
    
    async def list_donor_inbox(self, donor_id: str) -> Dict[str, List[BloodRequest]]:
        """Get donor inbox (targeted + discoverable requests)."""
        try:
            # Targeted requests (pending status, requestedTo = donor_id)
            targeted_cursor = self.collection.find({
                "requestedTo": donor_id,
                "status": "pending"
            }).sort("createdAt", -1)
            
            targeted = []
            async for doc in targeted_cursor:
                targeted.append(self._doc_to_request(doc))
            
            # Discoverable requests (open status, excluding donor's own requests)
            discoverable_cursor = self.collection.find({
                "status": "open",
                "createdBy": {"$ne": donor_id}  # Exclude donor's own requests
            }).sort("createdAt", -1)
            
            discoverable = []
            async for doc in discoverable_cursor:
                discoverable.append(self._doc_to_request(doc))
            
            logger.info(f"Found {len(targeted)} targeted and {len(discoverable)} discoverable requests for donor {donor_id}")
            return {
                "targeted": targeted,
                "discoverable": discoverable
            }
            
        except Exception as e:
            logger.error(f"Error getting donor inbox: {e}")
            raise
    
    async def get_donor_stats(self, donor_id: str) -> Dict[str, int]:
        """Get donor statistics."""
        try:
            # Count total requests targeted to this donor
            total_received = await self.collection.count_documents({"requestedTo": donor_id})
            
            # Count accepted requests
            accepted = await self.collection.count_documents({
                "requestedTo": donor_id,
                "status": "accepted"
            })
            
            # Count rejected requests
            rejected = await self.collection.count_documents({
                "requestedTo": donor_id,
                "status": "rejected"
            })
            
            stats = {
                "totalReceived": total_received,
                "accepted": accepted,
                "rejected": rejected
            }
            
            logger.info(f"Donor stats for {donor_id}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting donor stats: {e}")
            raise
    
    def _doc_to_request(self, doc: Dict[str, Any]) -> BloodRequest:
        """Convert MongoDB document to BloodRequest."""
        return BloodRequest(
            id=doc["id"],
            createdBy=doc["createdBy"],
            patientName=doc["patientName"],
            requiredBloodGroup=doc["requiredBloodGroup"],
            city=doc["city"],
            gender=doc.get("gender"),
            hospital=doc.get("hospital"),
            locationAddress=doc.get("locationAddress"),
            locationLat=doc.get("locationLat"),
            locationLng=doc.get("locationLng"),
            unitsRequired=doc.get("unitsRequired"),
            neededBy=doc.get("neededBy"),
            notes=doc.get("notes"),
            requestedTo=doc.get("requestedTo"),
            status=doc.get("status", "open"),
            createdAt=doc.get("createdAt")
        )
