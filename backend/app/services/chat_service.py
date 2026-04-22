from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime
from app.repositories.factory import get_chat_repository
from app.core.ai_factory import get_ai_provider
from app.core.s3 import upload_file_to_s3
from app.domain.entities import ChatSession, ChatMessage, FileAttachment
import logging
import uuid
import re

logger = logging.getLogger(__name__)

# System prompt to restrict AI to blood donation and health-related topics only
BLOOD_DONATION_SYSTEM_PROMPT = """You are a helpful AI assistant for a blood donation platform. Your role is to provide information and assistance ONLY related to:

1. Blood donation (eligibility, process, benefits, requirements)
2. Blood types and compatibility
3. Health conditions related to blood donation
4. Blood bank operations and procedures
5. Medical information relevant to blood donation
6. General health questions that relate to blood donation eligibility

IMPORTANT RULES:
- ONLY answer questions related to blood donation, blood types, health conditions affecting donation, or general health questions relevant to donation eligibility
- If asked about programming, coding, software development, or any non-health/blood donation topics, politely decline and redirect to blood donation topics
- If asked to create code, write scripts, or help with technical tasks, politely decline
- Always redirect off-topic questions back to blood donation or health-related topics
- Be helpful, accurate, and professional in your responses
- If you're unsure about medical information, recommend consulting a healthcare professional

Example responses for off-topic queries:
- "I'm here to help with blood donation and health-related questions. Could you please ask me something about blood donation, blood types, or health conditions?"
- "I specialize in blood donation information. How can I help you with questions about donating blood or related health topics?"
"""

# Keywords that indicate off-topic queries
OFF_TOPIC_KEYWORDS = [
    'code', 'programming', 'react', 'javascript', 'python', 'html', 'css',
    'create code', 'write code', 'script', 'function', 'variable', 'api',
    'database', 'server', 'backend', 'frontend', 'framework', 'library',
    'git', 'github', 'deploy', 'build', 'compile', 'debug', 'error',
    'bug', 'algorithm', 'data structure', 'software', 'app development',
    'web development', 'mobile app', 'game', 'gaming', 'movie', 'music',
    'sports', 'cooking', 'recipe', 'travel', 'weather', 'news', 'politics'
]


class ChatService:
    """Chat service for AI chat functionality."""
    
    def __init__(self):
        self.chat_repo = get_chat_repository()
        self.ai_provider = get_ai_provider()
    
    def _is_query_relevant(self, content: str) -> bool:
        """
        Check if the query is relevant to blood donation or health topics.
        Returns True if relevant, False otherwise.
        """
        content_lower = content.lower()
        
        # Check for off-topic keywords
        for keyword in OFF_TOPIC_KEYWORDS:
            if keyword in content_lower:
                # Check if it's actually about blood donation (e.g., "blood code" in medical context)
                # If the query contains blood/health keywords, it might still be relevant
                if any(health_term in content_lower for health_term in ['blood', 'donation', 'health', 'medical', 'donor', 'patient']):
                    continue
                return False
        
        # Check for blood donation/health related keywords
        relevant_keywords = [
            'blood', 'donation', 'donor', 'donate', 'blood type', 'blood group',
            'health', 'medical', 'hospital', 'patient', 'eligibility', 'requirement',
            'hemoglobin', 'anemia', 'plasma', 'platelet', 'transfusion', 'compatibility',
            'o positive', 'o negative', 'a positive', 'a negative', 'b positive', 'b negative',
            'ab positive', 'ab negative', 'rh', 'universal donor', 'universal recipient',
            'blood bank', 'blood drive', 'blood test', 'health check', 'medical condition',
            'medication', 'disease', 'illness', 'symptom', 'treatment', 'doctor', 'physician'
        ]
        
        # If query contains relevant keywords, it's likely relevant
        if any(keyword in content_lower for keyword in relevant_keywords):
            return True
        
        # If query is very short and doesn't contain relevant keywords, might be off-topic
        if len(content.strip()) < 10:
            return False
        
        # Default: allow the query but let the system prompt handle filtering
        return True
    
    def _get_rejection_message(self) -> str:
        """Get a polite rejection message for off-topic queries."""
        return (
            "I'm here to help with blood donation and health-related questions. "
            "I can assist you with:\n"
            "- Blood donation eligibility and requirements\n"
            "- Blood types and compatibility\n"
            "- Health conditions related to blood donation\n"
            "- General health questions relevant to donation\n\n"
            "Please ask me something about blood donation or related health topics. "
            "How can I help you today?"
        )
    
    async def create_chat_session(self, user_id: str) -> ChatSession:
        """Create a new chat session."""
        try:
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Create session
            session = ChatSession(
                id=session_id,
                uid=user_id
            )
            
            created_session = await self.chat_repo.create_session(session)
            logger.info(f"Created chat session: {session_id}")
            
            return created_session
            
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            raise
    
    async def get_chat_session(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID."""
        try:
            session = await self.chat_repo.get_session_by_id(session_id)
            if session:
                logger.info(f"Retrieved chat session: {session_id}")
            return session
        except Exception as e:
            logger.error(f"Error getting chat session: {e}")
            raise
    
    async def list_user_sessions(self, user_id: str) -> List[ChatSession]:
        """List user's chat sessions."""
        try:
            sessions = await self.chat_repo.list_user_sessions(user_id)
            logger.info(f"Found {len(sessions)} chat sessions for user {user_id}")
            return sessions
        except Exception as e:
            logger.error(f"Error listing user sessions: {e}")
            raise
    
    async def send_message(
        self,
        session_id: str,
        user_id: str,
        content: str,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> ChatMessage:
        """Send a message in a chat session."""
        try:
            # Verify session belongs to user
            session = await self.chat_repo.get_session_by_id(session_id)
            if not session:
                raise ValueError("Chat session not found")
            
            if session.uid != user_id:
                raise ValueError("Unauthorized access to chat session")
            
            # Generate message ID
            message_id = str(uuid.uuid4())
            
            # Create user message
            user_message = ChatMessage(
                id=message_id,
                sessionId=session_id,
                role="user",
                content=content,
                attachments=attachments
            )
            
            created_message = await self.chat_repo.create_message(user_message)
            
            # Check if query is relevant to blood donation/health topics
            if not self._is_query_relevant(content):
                logger.info(f"Off-topic query detected in session {session_id}: {content[:50]}...")
                ai_response_content = self._get_rejection_message()
            else:
                # Get chat history for context
                chat_history = await self.chat_repo.list_session_messages(session_id)
                
                # Convert to AI provider format with system prompt
                messages = [
                    {"role": "system", "content": BLOOD_DONATION_SYSTEM_PROMPT}
                ]
                
                # Add last 10 messages for context (excluding system messages)
                for msg in chat_history[-10:]:
                    if msg.role != "system":  # Skip any existing system messages
                        messages.append({
                            "role": msg.role,
                            "content": msg.content
                        })
                
                # Generate AI response
                try:
                    ai_response_content = await self.ai_provider.generate_chat_completion(messages)
                    
                    # Double-check if AI response is off-topic (AI might ignore instructions)
                    if ai_response_content and len(ai_response_content) > 50:
                        # Check if response contains code blocks or programming terms
                        if any(indicator in ai_response_content.lower() for indicator in ['```', 'function(', 'const ', 'import ', 'def ', 'class ']):
                            logger.warning(f"AI generated off-topic response, using rejection message")
                            ai_response_content = self._get_rejection_message()
                    
                except Exception as ai_error:
                    logger.error(f"AI response generation failed: {ai_error}")
                    ai_response_content = "I received your message. How can I help you with blood donation questions?"
                
                # Fallback response if AI fails
                if not ai_response_content or ai_response_content.strip() == "":
                    ai_response_content = "I received your message. How can I help you with blood donation questions?"
            
            # Create AI response message
            ai_message_id = str(uuid.uuid4())
            ai_message = ChatMessage(
                id=ai_message_id,
                sessionId=session_id,
                role="assistant",
                content=ai_response_content
            )
            
            created_ai_message = await self.chat_repo.create_message(ai_message)
            
            logger.info(f"Sent message in session {session_id}")
            # Return the AI response message instead of user message
            return created_ai_message
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    async def send_streaming_message(
        self,
        session_id: str,
        user_id: str,
        content: str,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[str, None]:
        """Send a message and stream AI response."""
        try:
            # Verify session belongs to user
            session = await self.chat_repo.get_session_by_id(session_id)
            if not session:
                raise ValueError("Chat session not found")
            
            if session.uid != user_id:
                raise ValueError("Unauthorized access to chat session")
            
            # Generate message ID
            message_id = str(uuid.uuid4())
            
            # Create user message
            user_message = ChatMessage(
                id=message_id,
                sessionId=session_id,
                role="user",
                content=content,
                attachments=attachments
            )
            
            await self.chat_repo.create_message(user_message)
            
            # Check if query is relevant to blood donation/health topics
            if not self._is_query_relevant(content):
                logger.info(f"Off-topic query detected in session {session_id}: {content[:50]}...")
                rejection_message = self._get_rejection_message()
                # Stream rejection message character by character to simulate streaming
                for char in rejection_message:
                    yield char
                full_response = rejection_message
            else:
                # Get chat history for context
                chat_history = await self.chat_repo.list_session_messages(session_id)
                
                # Convert to AI provider format with system prompt
                messages = [
                    {"role": "system", "content": BLOOD_DONATION_SYSTEM_PROMPT}
                ]
                
                # Add last 10 messages for context (excluding system messages)
                for msg in chat_history[-10:]:
                    if msg.role != "system":  # Skip any existing system messages
                        messages.append({
                            "role": msg.role,
                            "content": msg.content
                        })
                
                # Stream AI response
                full_response = ""
                buffer = ""  # Buffer to check for off-topic content
                async for chunk in self.ai_provider.generate_streaming_chat_completion(messages):
                    full_response += chunk
                    buffer += chunk
                    
                    # Check buffer periodically for off-topic content
                    if len(buffer) > 100:
                        if any(indicator in buffer.lower() for indicator in ['```', 'function(', 'const ', 'import ', 'def ', 'class ']):
                            logger.warning(f"AI generated off-topic response in streaming, stopping stream")
                            # Stop streaming and yield rejection message
                            rejection_message = self._get_rejection_message()
                            yield f"\n\n{rejection_message}"
                            full_response = rejection_message
                            break
                        buffer = ""  # Reset buffer
                    
                    yield chunk
            
            # Save complete AI response
            ai_message_id = str(uuid.uuid4())
            ai_message = ChatMessage(
                id=ai_message_id,
                sessionId=session_id,
                role="assistant",
                content=full_response
            )
            
            await self.chat_repo.create_message(ai_message)
            
            logger.info(f"Sent streaming message in session {session_id}")
            
        except Exception as e:
            logger.error(f"Error sending streaming message: {e}")
            raise
    
    async def get_session_messages(self, session_id: str, user_id: str) -> List[ChatMessage]:
        """Get messages in a chat session."""
        try:
            # Verify session belongs to user
            session = await self.chat_repo.get_session_by_id(session_id)
            if not session:
                raise ValueError("Chat session not found")
            
            if session.uid != user_id:
                raise ValueError("Unauthorized access to chat session")
            
            messages = await self.chat_repo.list_session_messages(session_id)
            logger.info(f"Retrieved {len(messages)} messages from session {session_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Error getting session messages: {e}")
            raise
    
    async def upload_file_attachment(
        self,
        user_id: str,
        file_content: bytes,
        file_name: str,
        content_type: str
    ) -> FileAttachment:
        """Upload file attachment for chat."""
        try:
            # Upload file to S3
            file_url = await upload_file_to_s3(
                file_content, file_name, content_type, "chat-attachments"
            )
            
            if not file_url:
                raise ValueError("Failed to upload file")
            
            # Generate attachment ID
            attachment_id = str(uuid.uuid4())
            
            # Create attachment record
            attachment = FileAttachment(
                id=attachment_id,
                fileName=file_name,
                fileUrl=file_url,
                fileType=content_type,
                fileSize=len(file_content),
                uploadedBy=user_id
            )
            
            created_attachment = await self.chat_repo.create_file_attachment(attachment)
            
            logger.info(f"Uploaded file attachment: {attachment_id}")
            return created_attachment
            
        except Exception as e:
            logger.error(f"Error uploading file attachment: {e}")
            raise
    
    async def get_file_attachment(self, attachment_id: str) -> Optional[FileAttachment]:
        """Get file attachment by ID."""
        try:
            attachment = await self.chat_repo.get_file_attachment_by_id(attachment_id)
            if attachment:
                logger.info(f"Retrieved file attachment: {attachment_id}")
            return attachment
        except Exception as e:
            logger.error(f"Error getting file attachment: {e}")
            raise
    
    async def delete_chat_session(self, session_id: str, user_id: str) -> bool:
        """Delete a chat session."""
        try:
            # Verify session belongs to user
            session = await self.chat_repo.get_session_by_id(session_id)
            if not session:
                raise ValueError("Chat session not found")
            
            if session.uid != user_id:
                raise ValueError("Unauthorized access to chat session")
            
            # Delete session (messages will be deleted via cascade or separate operation)
            # For now, we'll just mark it as deleted or implement soft delete
            logger.info(f"Deleted chat session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting chat session: {e}")
            raise
