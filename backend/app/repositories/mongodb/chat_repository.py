from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.repositories.base import IChatRepository
from app.domain.entities import ChatSession, ChatMessage, FileAttachment
import logging

logger = logging.getLogger(__name__)


class MongoChatRepository(IChatRepository):
    """MongoDB implementation of chat repository."""
    
    def __init__(self):
        self._db = None
        self._sessions = None
        self._messages = None
        self._attachments = None
    
    @property
    def db(self):
        """Lazy-load database connection."""
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def sessions(self):
        """Lazy-load sessions collection."""
        if self._sessions is None:
            self._sessions = self.db.chat_sessions
        return self._sessions
    
    @property
    def messages(self):
        """Lazy-load messages collection."""
        if self._messages is None:
            self._messages = self.db.chat_messages
        return self._messages
    
    @property
    def attachments(self):
        """Lazy-load attachments collection."""
        if self._attachments is None:
            self._attachments = self.db.file_attachments
        return self._attachments
    
    # Chat Sessions
    async def create_session(self, session: ChatSession) -> ChatSession:
        """Create a new chat session."""
        try:
            session_dict = {
                "id": session.id,
                "uid": session.uid,
                "createdAt": session.createdAt,
                "updatedAt": session.updatedAt
            }
            
            result = await self.sessions.insert_one(session_dict)
            if result.inserted_id:
                logger.info(f"Chat session created successfully: {session.id}")
                return session
            else:
                raise Exception("Failed to create chat session")
                
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            raise
    
    async def get_session_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID."""
        try:
            session_doc = await self.sessions.find_one({"id": session_id})
            if session_doc:
                return self._doc_to_session(session_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting chat session by ID: {e}")
            raise
    
    async def list_user_sessions(self, user_id: str) -> List[ChatSession]:
        """List user's chat sessions."""
        try:
            cursor = self.sessions.find({"uid": user_id}).sort("updatedAt", -1)
            sessions = []
            async for doc in cursor:
                sessions.append(self._doc_to_session(doc))
            
            logger.info(f"Found {len(sessions)} chat sessions for user {user_id}")
            return sessions
            
        except Exception as e:
            logger.error(f"Error listing user chat sessions: {e}")
            raise
    
    # Chat Messages
    async def create_message(self, message: ChatMessage) -> ChatMessage:
        """Create a new chat message."""
        try:
            message_dict = {
                "id": message.id,
                "sessionId": message.sessionId,
                "role": message.role,
                "content": message.content,
                "attachments": message.attachments,
                "createdAt": message.createdAt
            }
            
            # Remove None values
            message_dict = {k: v for k, v in message_dict.items() if v is not None}
            
            result = await self.messages.insert_one(message_dict)
            if result.inserted_id:
                # Update session's updatedAt timestamp
                await self.sessions.update_one(
                    {"id": message.sessionId},
                    {"$set": {"updatedAt": datetime.utcnow()}}
                )
                
                logger.info(f"Chat message created successfully: {message.id}")
                return message
            else:
                raise Exception("Failed to create chat message")
                
        except Exception as e:
            logger.error(f"Error creating chat message: {e}")
            raise
    
    async def get_message_by_id(self, message_id: str) -> Optional[ChatMessage]:
        """Get chat message by ID."""
        try:
            message_doc = await self.messages.find_one({"id": message_id})
            if message_doc:
                return self._doc_to_message(message_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting chat message by ID: {e}")
            raise
    
    async def list_session_messages(self, session_id: str) -> List[ChatMessage]:
        """List messages in a session."""
        try:
            cursor = self.messages.find({"sessionId": session_id}).sort("createdAt", 1)
            messages = []
            async for doc in cursor:
                messages.append(self._doc_to_message(doc))
            
            logger.info(f"Found {len(messages)} messages in session {session_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Error listing session messages: {e}")
            raise
    
    # File Attachments
    async def create_file_attachment(self, attachment: FileAttachment) -> FileAttachment:
        """Create a new file attachment."""
        try:
            attachment_dict = {
                "id": attachment.id,
                "fileName": attachment.fileName,
                "fileUrl": attachment.fileUrl,
                "fileType": attachment.fileType,
                "fileSize": attachment.fileSize,
                "uploadedBy": attachment.uploadedBy,
                "createdAt": attachment.createdAt
            }
            
            result = await self.attachments.insert_one(attachment_dict)
            if result.inserted_id:
                logger.info(f"File attachment created successfully: {attachment.id}")
                return attachment
            else:
                raise Exception("Failed to create file attachment")
                
        except Exception as e:
            logger.error(f"Error creating file attachment: {e}")
            raise
    
    async def get_file_attachment_by_id(self, attachment_id: str) -> Optional[FileAttachment]:
        """Get file attachment by ID."""
        try:
            attachment_doc = await self.attachments.find_one({"id": attachment_id})
            if attachment_doc:
                return self._doc_to_attachment(attachment_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting file attachment by ID: {e}")
            raise
    
    def _doc_to_session(self, doc: Dict[str, Any]) -> ChatSession:
        """Convert MongoDB document to ChatSession."""
        return ChatSession(
            id=doc["id"],
            uid=doc["uid"],
            createdAt=doc.get("createdAt"),
            updatedAt=doc.get("updatedAt")
        )
    
    def _doc_to_message(self, doc: Dict[str, Any]) -> ChatMessage:
        """Convert MongoDB document to ChatMessage."""
        return ChatMessage(
            id=doc["id"],
            sessionId=doc["sessionId"],
            role=doc["role"],
            content=doc["content"],
            attachments=doc.get("attachments"),
            createdAt=doc.get("createdAt")
        )
    
    def _doc_to_attachment(self, doc: Dict[str, Any]) -> FileAttachment:
        """Convert MongoDB document to FileAttachment."""
        return FileAttachment(
            id=doc["id"],
            fileName=doc["fileName"],
            fileUrl=doc["fileUrl"],
            fileType=doc["fileType"],
            fileSize=doc["fileSize"],
            uploadedBy=doc["uploadedBy"],
            createdAt=doc.get("createdAt")
        )
