from typing import Optional, List, Dict, Any
from datetime import datetime
from app.repositories.factory import get_comment_repository
from app.domain.entities import Comment
import logging
import uuid

logger = logging.getLogger(__name__)


class CommentService:
    """Comment service for request comments management."""
    
    def __init__(self):
        self.comment_repo = get_comment_repository()
    
    async def create_comment(
        self,
        request_id: str,
        user_id: str,
        text: str
    ) -> Comment:
        """Create a new comment on a request."""
        try:
            # Generate comment ID
            comment_id = str(uuid.uuid4())
            
            # Create comment
            comment = Comment(
                id=comment_id,
                requestId=request_id,
                uid=user_id,
                text=text
            )
            
            created_comment = await self.comment_repo.create_comment(comment)
            logger.info(f"Created comment: {comment_id}")
            
            return created_comment
            
        except Exception as e:
            logger.error(f"Error creating comment: {e}")
            raise
    
    async def get_comment_by_id(self, comment_id: str) -> Optional[Comment]:
        """Get comment by ID."""
        try:
            comment = await self.comment_repo.get_comment_by_id(comment_id)
            if comment:
                logger.info(f"Retrieved comment: {comment_id}")
            return comment
        except Exception as e:
            logger.error(f"Error getting comment by ID: {e}")
            raise
    
    async def delete_comment(self, comment_id: str, user_id: str) -> bool:
        """Delete comment (only by author)."""
        try:
            # Get comment to check ownership
            comment = await self.comment_repo.get_comment_by_id(comment_id)
            if not comment:
                raise ValueError("Comment not found")
            
            # Check if user is the author
            if comment.uid != user_id:
                raise ValueError("Only the author can delete this comment")
            
            success = await self.comment_repo.delete_comment(comment_id)
            if success:
                logger.info(f"Deleted comment: {comment_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting comment: {e}")
            raise
    
    async def list_request_comments(self, request_id: str) -> List[Comment]:
        """List comments for a request."""
        try:
            comments = await self.comment_repo.list_request_comments(request_id)
            logger.info(f"Found {len(comments)} comments for request {request_id}")
            return comments
        except Exception as e:
            logger.error(f"Error listing request comments: {e}")
            raise
    
    async def update_comment(self, comment_id: str, user_id: str, new_text: str) -> Optional[Comment]:
        """Update comment (only by author)."""
        try:
            # Get comment to check ownership
            comment = await self.comment_repo.get_comment_by_id(comment_id)
            if not comment:
                raise ValueError("Comment not found")
            
            # Check if user is the author
            if comment.uid != user_id:
                raise ValueError("Only the author can update this comment")
            
            # Update comment
            update_data = {"text": new_text}
            updated_comment = await self.comment_repo.update_comment(comment_id, update_data)
            
            if updated_comment:
                logger.info(f"Updated comment: {comment_id}")
            
            return updated_comment
            
        except Exception as e:
            logger.error(f"Error updating comment: {e}")
            raise
