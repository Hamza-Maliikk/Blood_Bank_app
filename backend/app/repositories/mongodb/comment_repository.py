from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.repositories.base import ICommentRepository
from app.domain.entities import Comment
import logging

logger = logging.getLogger(__name__)


class MongoCommentRepository(ICommentRepository):
    """MongoDB implementation of comment repository."""
    
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.comments
    
    async def create_comment(self, comment: Comment) -> Comment:
        """Create a new comment."""
        try:
            comment_dict = {
                "id": comment.id,
                "requestId": comment.requestId,
                "uid": comment.uid,
                "text": comment.text,
                "createdAt": comment.createdAt
            }
            
            result = await self.collection.insert_one(comment_dict)
            if result.inserted_id:
                logger.info(f"Comment created successfully: {comment.id}")
                return comment
            else:
                raise Exception("Failed to create comment")
                
        except Exception as e:
            logger.error(f"Error creating comment: {e}")
            raise
    
    async def get_comment_by_id(self, comment_id: str) -> Optional[Comment]:
        """Get comment by ID."""
        try:
            comment_doc = await self.collection.find_one({"id": comment_id})
            if comment_doc:
                return self._doc_to_comment(comment_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting comment by ID: {e}")
            raise
    
    async def delete_comment(self, comment_id: str) -> bool:
        """Delete comment."""
        try:
            result = await self.collection.delete_one({"id": comment_id})
            success = result.deleted_count > 0
            if success:
                logger.info(f"Comment deleted successfully: {comment_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error deleting comment: {e}")
            raise
    
    async def list_request_comments(self, request_id: str) -> List[Comment]:
        """List comments for a request."""
        try:
            cursor = self.collection.find({"requestId": request_id}).sort("createdAt", 1)
            comments = []
            async for doc in cursor:
                comments.append(self._doc_to_comment(doc))
            
            logger.info(f"Found {len(comments)} comments for request {request_id}")
            return comments
            
        except Exception as e:
            logger.error(f"Error listing request comments: {e}")
            raise
    
    def _doc_to_comment(self, doc: Dict[str, Any]) -> Comment:
        """Convert MongoDB document to Comment."""
        return Comment(
            id=doc["id"],
            requestId=doc["requestId"],
            uid=doc["uid"],
            text=doc["text"],
            createdAt=doc.get("createdAt")
        )
