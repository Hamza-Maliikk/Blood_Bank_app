from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import openai
import google.generativeai as genai
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> str:
        """Generate a chat completion."""
        pass
    
    @abstractmethod
    async def generate_streaming_chat_completion(
        self,
        messages: List[Dict[str, str]]
    ):
        """Generate a streaming chat completion."""
        pass
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000
    ) -> str:
        """Generate text from a prompt."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI implementation of AI provider."""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> str:
        """Generate a chat completion using OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                stream=stream,
                max_tokens=1000,
                temperature=0.7
            )
            
            if stream:
                return response  # Return the stream object
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def generate_streaming_chat_completion(
        self,
        messages: List[Dict[str, str]]
    ):
        """Generate a streaming chat completion using OpenAI."""
        try:
            stream = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                stream=True,
                max_tokens=1000,
                temperature=0.7
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming API error: {e}")
            raise
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000
    ) -> str:
        """Generate text from a prompt using OpenAI."""
        try:
            # Use chat completions API instead of deprecated completions API
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant for a blood donation platform. Provide clear, helpful, and accurate responses."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI text generation error: {e}")
            raise


class GeminiProvider(AIProvider):
    """Google Gemini implementation of AI provider."""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> str:
        """Generate a chat completion using Gemini."""
        try:
            # Convert messages to Gemini format
            prompt = self._convert_messages_to_prompt(messages)
            
            if stream:
                response = self.model.generate_content_async(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=1000,
                        temperature=0.7
                    )
                )
                return response  # Return the response object
            else:
                response = await self.model.generate_content_async(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=1000,
                        temperature=0.7
                    )
                )
                return response.text
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    async def generate_streaming_chat_completion(
        self,
        messages: List[Dict[str, str]]
    ):
        """Generate a streaming chat completion using Gemini."""
        try:
            # Convert messages to Gemini format
            prompt = self._convert_messages_to_prompt(messages)
            
            # Note: Gemini doesn't support true streaming like OpenAI
            # We'll simulate streaming by chunking the response
            response = await self.model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1000,
                    temperature=0.7
                )
            )
            
            # Simulate streaming by yielding chunks
            text = response.text
            chunk_size = 50
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                yield chunk
                
        except Exception as e:
            logger.error(f"Gemini streaming API error: {e}")
            raise
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000
    ) -> str:
        """Generate text from a prompt using Gemini."""
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7
                )
            )
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini text generation error: {e}")
            raise
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to a single prompt for Gemini."""
        prompt_parts = []
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n".join(prompt_parts)


class AIProviderFactory:
    """Factory for creating AI providers."""
    
    @staticmethod
    def create_provider() -> AIProvider:
        """Create an AI provider based on configuration."""
        if settings.AI_PROVIDER == "openai":
            return OpenAIProvider()
        elif settings.AI_PROVIDER == "gemini":
            return GeminiProvider()
        else:
            raise ValueError(f"Unsupported AI provider: {settings.AI_PROVIDER}")


# Global AI provider instance
ai_provider: Optional[AIProvider] = None


def get_ai_provider() -> AIProvider:
    """Get the global AI provider instance."""
    global ai_provider
    if ai_provider is None:
        ai_provider = AIProviderFactory.create_provider()
    return ai_provider
