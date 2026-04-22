from typing import Optional, List, Dict, Any
from app.core.ai_factory import get_ai_provider
from app.repositories.factory import get_user_repository, get_request_repository
import logging

logger = logging.getLogger(__name__)


class AIService:
    """AI service for enhanced search, recommendations, and content generation."""
    
    def __init__(self):
        self.ai_provider = get_ai_provider()
        self.user_repo = get_user_repository()
        self.request_repo = get_request_repository()
    
    async def enhanced_search(
        self,
        query: str,
        search_type: str = "general",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform AI-enhanced search."""
        try:
            # Build context-aware prompt
            context = await self._build_search_context(user_id, search_type)
            
            prompt = f"""
            Context: {context}
            
            User Query: {query}
            Search Type: {search_type}
            
            Please provide a comprehensive search result that includes:
            1. Relevant information based on the query
            2. Suggestions for related searches
            3. Helpful tips or recommendations
            
            Format your response as a structured JSON with sections for:
            - summary: Brief summary of findings
            - results: List of relevant items
            - suggestions: Related search suggestions
            - tips: Helpful tips or recommendations
            """
            
            response = await self.ai_provider.generate_text(prompt, max_tokens=1000)
            
            logger.info(f"Performed AI-enhanced search for query: {query}")
            
            # Parse response (in a real implementation, you'd want better JSON parsing)
            return {
                "query": query,
                "search_type": search_type,
                "response": response,
                "content": response,
                "timestamp": "2024-01-01T00:00:00Z"  # You'd use actual timestamp
            }
            
        except Exception as e:
            logger.error(f"Error performing enhanced search: {e}")
            # Return fallback response
            return {
                "query": query,
                "search_type": search_type,
                "response": f"I can help you with blood donation questions. For '{query}', here are some general tips: Check your local blood bank, maintain good health, and stay hydrated.",
                "content": f"I can help you with blood donation questions. For '{query}', here are some general tips: Check your local blood bank, maintain good health, and stay hydrated.",
                "timestamp": "2024-01-01T00:00:00Z"
            }
    
    async def get_personalized_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get personalized recommendations for user."""
        try:
            # Get user profile
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Get user's request history
            user_requests = await self.request_repo.list_user_requests(user_id)
            
            # Get donor statistics if user is a donor
            donor_stats = {}
            if user.mode == "donor":
                donor_stats = await self.request_repo.get_donor_stats(user_id)
            
            # Build context for recommendations
            context = f"""
            User Profile:
            - Name: {user.name}
            - Mode: {user.mode}
            - Blood Group: {user.bloodGroup}
            - City: {user.city}
            - Available as Donor: {user.available}
            
            User Activity:
            - Total Requests Created: {len(user_requests)}
            - Donor Statistics: {donor_stats}
            """
            
            prompt = f"""
            Based on the following user profile and activity, provide personalized recommendations:
            
            {context}
            
            Please provide recommendations for:
            1. Blood donation opportunities (if user is a donor)
            2. Request optimization tips (if user is a patient)
            3. Profile improvement suggestions
            4. General platform usage tips
            
            Format as JSON with sections for:
            - donation_opportunities: List of relevant opportunities
            - optimization_tips: Tips for better platform usage
            - profile_suggestions: Suggestions for profile improvement
            - general_tips: General platform tips
            """
            
            response = await self.ai_provider.generate_text(prompt, max_tokens=1000)
            
            logger.info(f"Generated personalized recommendations for user: {user_id}")
            
            return {
                "user_id": user_id,
                "recommendations": response,
                "insights": f"Welcome {user.name}! Based on your {user.mode} profile, here are some personalized recommendations for you.",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
        except Exception as e:
            logger.error(f"Error generating personalized recommendations: {e}")
            # Return fallback recommendations
            return {
                "user_id": user_id,
                "recommendations": "Welcome to Blood Bank! Here are some general recommendations: Keep your profile updated, check for urgent requests regularly, and maintain good communication with other users.",
                "insights": "Welcome to Blood Bank! Here are some general recommendations to help you get started.",
                "timestamp": "2024-01-01T00:00:00Z"
            }
    
    async def generate_content(
        self,
        content_type: str,
        context: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> str:
        """Generate content using AI."""
        try:
            # Build context-aware prompt based on content type
            if content_type == "request_description":
                prompt = self._build_request_description_prompt(context)
            elif content_type == "donor_profile":
                prompt = self._build_donor_profile_prompt(context)
            elif content_type == "notification_message":
                prompt = self._build_notification_prompt(context)
            else:
                prompt = f"Generate {content_type} content based on: {context}"
            
            response = await self.ai_provider.generate_text(prompt, max_tokens=500)
            
            logger.info(f"Generated {content_type} content")
            return response
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            # Return fallback content based on type
            if content_type == "request_suggestion":
                return f"I can help you create a blood request. What blood group do you need?"
            elif content_type == "donor_recommendation":
                return f"I can help you find suitable donors. What blood group and city are you looking for?"
            elif content_type == "blood_info":
                blood_group = context.get('blood_group', 'your blood group')
                return f"Here's information about blood group {blood_group}. Blood groups are important for compatibility in transfusions."
            else:
                return f"I can help you with {content_type}. Please provide more details about what you need."
    
    async def analyze_platform_health(self) -> Dict[str, Any]:
        """Analyze platform health and provide insights."""
        try:
            # Get platform statistics
            all_users = await self.user_repo.list_all_users(limit=1000)
            all_requests = await self.request_repo.list_requests(limit=1000)
            
            # Calculate basic metrics
            total_users = len(all_users)
            active_donors = len([u for u in all_users if u.mode == "donor" and u.available])
            total_requests = len(all_requests)
            fulfilled_requests = len([r for r in all_requests if r.status == "fulfilled"])
            
            context = f"""
            Platform Statistics:
            - Total Users: {total_users}
            - Active Donors: {active_donors}
            - Total Requests: {total_requests}
            - Fulfilled Requests: {fulfilled_requests}
            - Fulfillment Rate: {(fulfilled_requests/total_requests*100) if total_requests > 0 else 0:.1f}%
            """
            
            prompt = f"""
            Analyze the following platform statistics and provide insights:
            
            {context}
            
            Please provide analysis on:
            1. Platform health indicators
            2. Areas for improvement
            3. Growth opportunities
            4. User engagement insights
            5. Recommendations for platform optimization
            
            Format as JSON with sections for:
            - health_indicators: Key health metrics
            - improvements: Areas needing improvement
            - opportunities: Growth opportunities
            - engagement: User engagement insights
            - recommendations: Actionable recommendations
            """
            
            response = await self.ai_provider.generate_text(prompt, max_tokens=1000)
            
            logger.info("Generated platform health analysis")
            
            return {
                "analysis": response,
                "metrics": {
                    "total_users": total_users,
                    "active_donors": active_donors,
                    "total_requests": total_requests,
                    "fulfilled_requests": fulfilled_requests
                },
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing platform health: {e}")
            raise
    
    async def _build_search_context(self, user_id: Optional[str], search_type: str) -> str:
        """Build context for search queries."""
        context = f"Search Type: {search_type}"
        
        if user_id:
            user = await self.user_repo.get_user_by_id(user_id)
            if user:
                context += f"\nUser: {user.name}, Mode: {user.mode}, City: {user.city}"
        
        return context
    
    def _build_request_description_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for request description generation."""
        return f"""
        Generate a compelling blood request description based on:
        - Patient: {context.get('patient_name', 'Unknown')}
        - Blood Group: {context.get('blood_group', 'Unknown')}
        - Location: {context.get('city', 'Unknown')}
        - Urgency: {context.get('urgency', 'Normal')}
        - Additional Info: {context.get('notes', 'None')}
        
        Make it empathetic, clear, and actionable.
        """
    
    def _build_donor_profile_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for donor profile generation."""
        return f"""
        Generate a donor profile description based on:
        - Name: {context.get('name', 'Unknown')}
        - Blood Group: {context.get('blood_group', 'Unknown')}
        - City: {context.get('city', 'Unknown')}
        - Experience: {context.get('experience', 'New donor')}
        
        Make it professional and encouraging.
        """
    
    def _build_notification_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for notification message generation."""
        return f"""
        Generate a notification message for:
        - Type: {context.get('type', 'general')}
        - Recipient: {context.get('recipient_type', 'user')}
        - Action: {context.get('action', 'notification')}
        - Context: {context.get('context', 'None')}
        
        Make it clear, concise, and actionable.
        """
