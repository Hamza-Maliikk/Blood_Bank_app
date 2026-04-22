from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.chat_service import ChatService
from app.core.security import get_current_user, get_current_user_id
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()
chat_service = ChatService()


# Request/Response Models
class StreamingMessageRequest(BaseModel):
    sessionId: str
    content: str
    attachments: Optional[List[Dict[str, Any]]] = None


async def generate_sse_stream(session_id: str, user_id: str, content: str, attachments: Optional[List[Dict[str, Any]]] = None):
    """Generate Server-Sent Events stream for AI chat responses."""
    try:
        # Send initial message
        yield f"data: {json.dumps({'type': 'start', 'message': 'Starting AI response...'})}\n\n"
        
        # Stream AI response
        async for chunk in chat_service.send_streaming_message(session_id, user_id, content, attachments):
            if chunk:
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                await asyncio.sleep(0.01)  # Small delay to prevent overwhelming the client
        
        # Send completion signal
        yield f"data: {json.dumps({'type': 'end', 'message': 'AI response complete'})}\n\n"
        
    except Exception as e:
        logger.error(f"SSE stream error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': 'An error occurred while generating response'})}\n\n"


@router.post("/stream")
async def stream_ai_response(
    request_data: StreamingMessageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Stream AI chat response using Server-Sent Events."""
    try:
        user_id = current_user["user_id"]
        
        # Verify session belongs to user
        session = await chat_service.get_chat_session(request_data.sessionId)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        if session.uid != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized access to chat session"
            )
        
        # Create streaming response
        return StreamingResponse(
            generate_sse_stream(
                session_id=request_data.sessionId,
                user_id=user_id,
                content=request_data.content,
                attachments=request_data.attachments
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stream AI response error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stream AI response"
        )


@router.get("/stream/{session_id}")
async def stream_session_messages(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Stream chat session messages using Server-Sent Events."""
    try:
        user_id = current_user["user_id"]
        
        # Verify session belongs to user
        session = await chat_service.get_chat_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        if session.uid != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized access to chat session"
            )
        
        async def generate_message_stream():
            """Generate stream of chat messages."""
            try:
                # Get existing messages
                messages = await chat_service.get_session_messages(session_id, user_id)
                
                # Send existing messages
                for message in messages:
                    yield f"data: {json.dumps({'type': 'message', 'data': message.__dict__})}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'type': 'complete', 'message': 'All messages loaded'})}\n\n"
                
            except Exception as e:
                logger.error(f"Message stream error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': 'Failed to load messages'})}\n\n"
        
        return StreamingResponse(
            generate_message_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stream session messages error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stream session messages"
        )
