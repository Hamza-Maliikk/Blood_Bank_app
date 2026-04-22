from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.chat_service import ChatService
from app.core.security import get_current_user, get_current_user_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
chat_service = ChatService()


# Request/Response Models
class ChatMessageSend(BaseModel):
    sessionId: str
    content: str
    attachments: Optional[List[Dict[str, Any]]] = None


@router.post("/sessions")
async def create_chat_session(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Create a new chat session."""
    try:
        user_id = current_user["user_id"]
        session = await chat_service.create_chat_session(user_id)
        
        return {
            "success": True,
            "data": session.__dict__,
            "message": "Chat session created successfully"
        }
        
    except RuntimeError as e:
        # Database not initialized
        logger.error(f"Database not initialized: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is not available. Please try again in a moment."
        )
    except Exception as e:
        logger.error(f"Create chat session error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chat session: {str(e)}"
        )


@router.get("/sessions")
async def list_user_sessions(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List user's chat sessions."""
    try:
        user_id = current_user["user_id"]
        sessions = await chat_service.list_user_sessions(user_id)
        
        return {
            "success": True,
            "data": [session.__dict__ for session in sessions]
        }
        
    except Exception as e:
        logger.error(f"List user sessions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list chat sessions"
        )


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    message_data: ChatMessageSend,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Send a message in a chat session."""
    try:
        user_id = current_user["user_id"]
        
        message = await chat_service.send_message(
            session_id=session_id,
            user_id=user_id,
            content=message_data.content,
            attachments=message_data.attachments
        )
        
        return {
            "success": True,
            "data": message.__dict__,
            "message": "Message sent successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send message error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get messages in a chat session."""
    try:
        user_id = current_user["user_id"]
        messages = await chat_service.get_session_messages(session_id, user_id)
        
        return {
            "success": True,
            "data": [message.__dict__ for message in messages]
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session messages error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session messages"
        )


@router.post("/upload")
async def upload_file_attachment(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Upload file attachment for chat."""
    try:
        user_id = current_user["user_id"]
        
        # Read file content
        file_content = await file.read()
        
        attachment = await chat_service.upload_file_attachment(
            user_id=user_id,
            file_content=file_content,
            file_name=file.filename,
            content_type=file.content_type
        )
        
        return {
            "success": True,
            "data": attachment.__dict__,
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Upload file attachment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )
