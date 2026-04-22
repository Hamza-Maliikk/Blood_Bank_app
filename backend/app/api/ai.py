from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.ai_service import AIService
from app.core.security import get_current_user, get_current_user_id, require_admin
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
ai_service = AIService()


# Request/Response Models
class AISearchRequest(BaseModel):
    query: str
    search_type: str = "general"


class ContentGenerateRequest(BaseModel):
    content_type: str
    context: Dict[str, Any]


@router.post("/search")
async def ai_enhanced_search(
    search_data: AISearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Perform AI-enhanced search."""
    try:
        user_id = current_user["user_id"]
        
        result = await ai_service.enhanced_search(
            query=search_data.query,
            search_type=search_data.search_type,
            user_id=user_id
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"AI enhanced search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform AI search"
        )


@router.get("/recommendations")
async def get_personalized_recommendations(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get personalized recommendations for user."""
    try:
        user_id = current_user["user_id"]
        
        recommendations = await ai_service.get_personalized_recommendations(user_id)
        
        return {
            "success": True,
            "data": recommendations
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Get personalized recommendations error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendations"
        )


@router.post("/generate-content")
async def generate_content(
    content_data: ContentGenerateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate content using AI."""
    try:
        user_id = current_user["user_id"]
        
        content = await ai_service.generate_content(
            content_type=content_data.content_type,
            context=content_data.context,
            user_id=user_id
        )
        
        return {
            "success": True,
            "data": {
                "content": content,
                "content_type": content_data.content_type
            }
        }
        
    except Exception as e:
        logger.error(f"Generate content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate content"
        )


@router.get("/platform-health")
async def analyze_platform_health(
    admin_user: Dict[str, Any] = Depends(require_admin)
):
    """Analyze platform health and provide insights (admin only)."""
    try:
        analysis = await ai_service.analyze_platform_health()
        
        return {
            "success": True,
            "data": analysis
        }
        
    except Exception as e:
        logger.error(f"Analyze platform health error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze platform health"
        )
