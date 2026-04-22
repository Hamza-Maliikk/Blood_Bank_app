from socketio import AsyncServer, ASGIApp
from app.core.security import verify_token
from app.core.config import settings
import logging



logger = logging.getLogger(__name__)

# Create Socket.IO server (ASGI mode for FastAPI)

sio = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
)

socket_app = ASGIApp(sio)

@sio.event
async def connect(sid, environ, auth):
    """Handle client connection."""
    try:
        # Extract token from auth or query parameters
        token = None
        if auth and "token" in auth:
            token = auth["token"]
        elif "HTTP_AUTHORIZATION" in environ:
            auth_header = environ["HTTP_AUTHORIZATION"]
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
        
        if not token:
            logger.warning(f"Connection rejected - no token: {sid}")
            return False
        
        # Verify token
        try:
            payload = verify_token(token)
            user_id = payload.get("sub")
            email = payload.get("email")
            
            if not user_id:
                logger.warning(f"Connection rejected - invalid token: {sid}")
                return False
            
            # Store user info in session
            await sio.save_session(sid, {
                "user_id": user_id,
                "email": email,
                "authenticated": True
            })
            
            # Join user to their personal room
            await sio.enter_room(sid, f"user_{user_id}")
            
            logger.info(f"User {user_id} connected: {sid}")
            
            # Send connection confirmation
            await sio.emit("connected", {
                "message": "Connected successfully",
                "user_id": user_id
            }, room=sid)
            
            return True
            
        except Exception as e:
            logger.warning(f"Connection rejected - token verification failed: {sid}, {e}")
            return False
            
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return False


@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    try:
        session = await sio.get_session(sid)
        if session and session.get("authenticated"):
            user_id = session.get("user_id")
            logger.info(f"User {user_id} disconnected: {sid}")
        else:
            logger.info(f"Anonymous user disconnected: {sid}")
    except Exception as e:
        logger.error(f"Disconnection error: {e}")


@sio.event
async def join_room(sid, data):
    """Join a specific room (e.g., request-specific room)."""
    try:
        session = await sio.get_session(sid)
        if not session or not session.get("authenticated"):
            await sio.emit("error", {"message": "Not authenticated"}, room=sid)
            return
        
        room = data.get("room")
        if not room:
            await sio.emit("error", {"message": "Room not specified"}, room=sid)
            return
        
        await sio.enter_room(sid, room)
        await sio.emit("joined_room", {"room": room}, room=sid)
        
        logger.info(f"User {session['user_id']} joined room {room}")
        
    except Exception as e:
        logger.error(f"Join room error: {e}")
        await sio.emit("error", {"message": "Failed to join room"}, room=sid)


@sio.event
async def leave_room(sid, data):
    """Leave a specific room."""
    try:
        session = await sio.get_session(sid)
        if not session or not session.get("authenticated"):
            await sio.emit("error", {"message": "Not authenticated"}, room=sid)
            return
        
        room = data.get("room")
        if not room:
            await sio.emit("error", {"message": "Room not specified"}, room=sid)
            return
        
        await sio.leave_room(sid, room)
        await sio.emit("left_room", {"room": room}, room=sid)
        
        logger.info(f"User {session['user_id']} left room {room}")
        
    except Exception as e:
        logger.error(f"Leave room error: {e}")
        await sio.emit("error", {"message": "Failed to leave room"}, room=sid)


# Event handlers for specific features
@sio.event
async def send_chat_message(sid, data):
    """Handle chat message sending."""
    try:
        session = await sio.get_session(sid)
        if not session or not session.get("authenticated"):
            await sio.emit("error", {"message": "Not authenticated"}, room=sid)
            return
        
        user_id = session["user_id"]
        session_id = data.get("session_id")
        content = data.get("content")
        
        if not session_id or not content:
            await sio.emit("error", {"message": "Missing session_id or content"}, room=sid)
            return
        
        # Emit message to chat session room
        await sio.emit("new_chat_message", {
            "user_id": user_id,
            "session_id": session_id,
            "content": content,
            "timestamp": "2024-01-01T00:00:00Z"  # You'd use actual timestamp
        }, room=f"chat_{session_id}")
        
        logger.info(f"Chat message sent by {user_id} in session {session_id}")
        
    except Exception as e:
        logger.error(f"Send chat message error: {e}")
        await sio.emit("error", {"message": "Failed to send message"}, room=sid)


@sio.event
async def request_update(sid, data):
    """Handle request status updates."""
    try:
        session = await sio.get_session(sid)
        if not session or not session.get("authenticated"):
            await sio.emit("error", {"message": "Not authenticated"}, room=sid)
            return
        
        user_id = session["user_id"]
        request_id = data.get("request_id")
        status = data.get("status")
        
        if not request_id or not status:
            await sio.emit("error", {"message": "Missing request_id or status"}, room=sid)
            return
        
        # Emit update to request room
        await sio.emit("request_status_update", {
            "request_id": request_id,
            "status": status,
            "updated_by": user_id,
            "timestamp": "2024-01-01T00:00:00Z"
        }, room=f"request_{request_id}")
        
        logger.info(f"Request {request_id} status updated to {status} by {user_id}")
        
    except Exception as e:
        logger.error(f"Request update error: {e}")
        await sio.emit("error", {"message": "Failed to update request"}, room=sid)


# Utility functions for emitting events from other parts of the application
async def emit_notification(user_id: str, notification_data: dict):
    """Emit notification to specific user."""
    try:
        await sio.emit("notification", notification_data, room=f"user_{user_id}")
        logger.info(f"Notification sent to user {user_id}")
    except Exception as e:
        logger.error(f"Emit notification error: {e}")


async def emit_request_notification(request_id: str, notification_data: dict):
    """Emit notification to request room."""
    try:
        await sio.emit("request_notification", notification_data, room=f"request_{request_id}")
        logger.info(f"Request notification sent for request {request_id}")
    except Exception as e:
        logger.error(f"Emit request notification error: {e}")


async def emit_donor_availability_update(user_id: str, available: bool):
    """Emit donor availability update."""
    try:
        await sio.emit("donor_availability_update", {
            "user_id": user_id,
            "available": available,
            "timestamp": "2024-01-01T00:00:00Z"
        }, room=f"user_{user_id}")
        
        # Also broadcast to general donors room
        await sio.emit("donor_availability_update", {
            "user_id": user_id,
            "available": available,
            "timestamp": "2024-01-01T00:00:00Z"
        }, room="donors")
        
        logger.info(f"Donor availability update sent for user {user_id}")
    except Exception as e:
        logger.error(f"Emit donor availability update error: {e}")


async def emit_chat_message(session_id: str, message_data: dict):
    """Emit chat message to session room."""
    try:
        await sio.emit("new_chat_message", message_data, room=f"chat_{session_id}")
        logger.info(f"Chat message emitted for session {session_id}")
    except Exception as e:
        logger.error(f"Emit chat message error: {e}")


async def emit_ai_response(session_id: str, response_data: dict):
    """Emit AI response to chat session."""
    try:
        await sio.emit("ai_response", response_data, room=f"chat_{session_id}")
        logger.info(f"AI response emitted for session {session_id}")
    except Exception as e:
        logger.error(f"Emit AI response error: {e}")
