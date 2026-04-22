from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.comment_service import CommentService
from app.core.security import get_current_user, get_current_user_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
comment_service = CommentService()


# Request/Response Models
class CommentCreate(BaseModel):
    requestId: str
    text: str


class CommentUpdate(BaseModel):
    text: str


@router.post("/")
async def create_comment(
    comment_data: CommentCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new comment on a request."""
    try:
        user_id = current_user["user_id"]
        
        comment = await comment_service.create_comment(
            request_id=comment_data.requestId,
            user_id=user_id,
            text=comment_data.text
        )
        
        return {
            "success": True,
            "data": comment.__dict__,
            "message": "Comment created successfully"
        }
        
    except Exception as e:
        logger.error(f"Create comment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create comment"
        )


@router.get("/{request_id}")
async def list_request_comments(request_id: str):
    """List comments for a request."""
    try:
        comments = await comment_service.list_request_comments(request_id)
        
        return {
            "success": True,
            "data": [comment.__dict__ for comment in comments]
        }
        
    except Exception as e:
        logger.error(f"List request comments error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list comments"
        )


@router.put("/{comment_id}")
async def update_comment(
    comment_id: str,
    comment_data: CommentUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update comment (only by author)."""
    try:
        user_id = current_user["user_id"]
        
        updated_comment = await comment_service.update_comment(
            comment_id=comment_id,
            user_id=user_id,
            new_text=comment_data.text
        )
        
        if not updated_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        return {
            "success": True,
            "data": updated_comment.__dict__,
            "message": "Comment updated successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update comment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update comment"
        )


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete comment (only by author)."""
    try:
        user_id = current_user["user_id"]
        
        success = await comment_service.delete_comment(comment_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        return {
            "success": True,
            "message": "Comment deleted successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete comment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete comment"
        )
