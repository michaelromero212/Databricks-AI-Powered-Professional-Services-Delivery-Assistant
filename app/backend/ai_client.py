import os
import requests
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()


class AIClient:
    """Client for Hugging Face Inference API using huggingface_hub."""
    
    # Prompt templates for PS insights
    PROMPT_TEMPLATES = {
        "health_summary": "Analyze this Professional Services engagement and provide a concise 2-3 sentence health summary. \n\nEngagement: {customer_name}\nType: {engagement_type}\nStatus: {status}\nHealth Score: {health_score}/100\nTasks: {completed_tasks}/{total_tasks} completed\nRecent Observations: {recent_notes}",
        
        "risk_detection": "Identify risk signals (scope creep, resource issues, timeline concerns, blockers) in these delivery notes for {customer_name}. \n\nDelivery Notes:\n{delivery_notes}\n\nList any risks found or state 'No significant risks identified.'",
        
        "theme_extraction": "Extract 3-5 recurring themes from these delivery notes for {customer_name}. Format as bullet points. \n\nNotes:\n{all_notes}",
        
        "action_recommendation": "Recommend 2-3 specific, high-priority next actions for the delivery manager based on this status:\n\nCustomer: {customer_name}\nStatus: {status}\nHealth Score: {health_score}/100\nCurrent Phase: {current_phase}\nKey Concerns: {concerns}"
    }
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize the AI client.
        
        Args:
            api_token: Hugging Face API token. If not provided, reads from
                       HUGGINGFACE_API_TOKEN environment variable.
        """
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_TOKEN")
        
        if not self.api_token:
            raise ValueError(
                "Hugging Face API token required. Set HUGGINGFACE_API_TOKEN "
                "environment variable or pass api_token parameter."
            )
        
        # Ensure token is not logged
        if len(self.api_token) < 10:
            raise ValueError("Invalid API token format")
        
        self.model_id = "mistralai/Mistral-7B-Instruct-v0.2"
        self.client = InferenceClient(model=self.model_id, token=self.api_token)
    
    def _query(self, prompt: str, max_tokens: int = 256) -> str:
        """Send prompt to Hugging Face via InferenceClient chat_completion.
        
        Args:
            prompt: The text prompt
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg:
                return "Error: Invalid API token."
            elif "503" in error_msg:
                return "Error: Model is loading. Please try again in a moment."
            return f"Error: {error_msg}"

    
    def generate_insight(self, insight_type: str, engagement_data: dict) -> dict:
        """Generate a specific insight type for an engagement.
        
        Args:
            insight_type: One of 'health_summary', 'risk_detection', 
                         'theme_extraction', 'action_recommendation'
            engagement_data: Dictionary with engagement details
            
        Returns:
            Dictionary with insight details
        """
        template = self.PROMPT_TEMPLATES.get(insight_type)
        if not template:
            return {
                "success": False,
                "error": f"Unknown insight type: {insight_type}",
                "content": None
            }
        
        # Set defaults for missing fields
        defaults = {
            "customer_name": "Unknown",
            "engagement_type": "Unknown",
            "status": "Unknown",
            "health_score": 0,
            "days_remaining": 0,
            "completed_tasks": 0,
            "total_tasks": 0,
            "recent_notes": "No notes available",
            "delivery_notes": "No notes available",
            "all_notes": "No notes available",
            "current_phase": "Unknown",
            "concerns": "None specified"
        }
        
        # Merge with provided data
        data = {**defaults, **engagement_data}
        
        # Format the prompt
        try:
            prompt = template.format(**data)
        except KeyError as e:
            return {
                "success": False,
                "error": f"Missing required field: {e}",
                "content": None
            }
        
        # Query the LLM
        response = self._query(prompt)
        
        is_error = response.startswith("Error:")
        
        return {
            "success": not is_error,
            "insight_type": insight_type,
            "engagement_id": data.get("engagement_id"),
            "customer_name": data.get("customer_name"),
            "generated_at": datetime.now().isoformat(),
            "content": response if not is_error else None,
            "error": response if is_error else None
        }
    
    def generate_health_summary(self, engagement_data: dict) -> dict:
        """Generate a health summary for an engagement."""
        return self.generate_insight("health_summary", engagement_data)
    
    def generate_risk_detection(self, engagement_data: dict) -> dict:
        """Detect risks in engagement delivery notes."""
        return self.generate_insight("risk_detection", engagement_data)
    
    def generate_theme_extraction(self, engagement_data: dict) -> dict:
        """Extract themes from engagement notes."""
        return self.generate_insight("theme_extraction", engagement_data)
    
    def generate_action_recommendation(self, engagement_data: dict) -> dict:
        """Generate recommended actions for an engagement."""
        return self.generate_insight("action_recommendation", engagement_data)
    
    def generate_full_analysis(self, engagement_data: dict) -> list:
        """Generate all insight types for an engagement.
        
        Args:
            engagement_data: Dictionary with engagement details
            
        Returns:
            List of insight dictionaries
        """
        insights = []
        for insight_type in self.PROMPT_TEMPLATES.keys():
            insight = self.generate_insight(insight_type, engagement_data)
            insights.append(insight)
        return insights
    
    def check_connection(self) -> dict:
        """Check if the API connection is working.
        
        Returns:
            Dictionary with connection status
        """
        try:
            # Simple test query using chat_completion
            response = self.client.chat_completion(
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1,
                temperature=0.1
            )
            
            if response:
                return {"connected": True, "model": self.model_id}
            else:
                return {"connected": False, "error": "Empty response"}
                
        except Exception as e:
            error_msg = str(e)
            # If it's a 503, it means it's connected but loading
            if "503" in error_msg:
                return {"connected": True, "model": self.model_id, "status": "loading"}
            return {"connected": False, "error": error_msg}


# Singleton instance for convenience
_client: Optional[AIClient] = None


def get_ai_client() -> AIClient:
    """Get or create the AI client singleton."""
    global _client
    if _client is None:
        _client = AIClient()
    return _client
