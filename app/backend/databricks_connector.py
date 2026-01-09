"""
Databricks Connector

Provides data access layer for PS Delivery Assistant.
Supports both local file mode (for development) and Databricks SQL (for production).
"""

import os
import json
from pathlib import Path
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class DatabricksConnector:
    """Data connector supporting local files and Databricks."""
    
    def __init__(self, mode: Optional[str] = None):
        """Initialize the connector.
        
        Args:
            mode: 'local' for file-based, 'databricks' for SQL connector.
                 Defaults to DATA_MODE environment variable or 'local'.
        """
        self.mode = mode or os.getenv("DATA_MODE", "local")
        self.data_path = Path(__file__).parent.parent.parent / "data" / "generated"
        
        # Cache for loaded data
        self._cache = {}
        self._cache_time = {}
        self._cache_ttl = 60  # seconds
        
        if self.mode == "databricks":
            self._init_databricks()
    
    def _init_databricks(self):
        """Initialize Databricks SQL connection."""
        host = os.getenv("DATABRICKS_HOST")
        token = os.getenv("DATABRICKS_TOKEN")
        
        if not host or not token:
            raise ValueError(
                "Databricks credentials required. Set DATABRICKS_HOST and "
                "DATABRICKS_TOKEN environment variables."
            )
        
        # Note: Actual Databricks SQL connector would be initialized here
        # For POC, we fall back to local mode
        print("Warning: Databricks SQL connector not fully implemented. Using local mode.")
        self.mode = "local"
    
    def _load_json(self, filename: str) -> list:
        """Load data from a JSON file with caching."""
        cache_key = filename
        now = datetime.now().timestamp()
        
        # Check cache
        if cache_key in self._cache:
            if now - self._cache_time.get(cache_key, 0) < self._cache_ttl:
                return self._cache[cache_key]
        
        # Load from file
        filepath = self.data_path / filename
        if not filepath.exists():
            return []
        
        with open(filepath, "r") as f:
            data = json.load(f)
        
        # Update cache
        self._cache[cache_key] = data
        self._cache_time[cache_key] = now
        
        return data
    
    def _save_json(self, filename: str, data: list):
        """Save data to a JSON file."""
        self.data_path.mkdir(parents=True, exist_ok=True)
        filepath = self.data_path / filename
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        # Invalidate cache
        if filename in self._cache:
            del self._cache[filename]
    
    # ----- Engagements -----
    
    def get_engagements(self, status: Optional[str] = None) -> list:
        """Get all engagements, optionally filtered by status."""
        engagements = self._load_json("engagements.json")
        
        if status:
            engagements = [e for e in engagements if e.get("status") == status]
        
        return sorted(engagements, key=lambda x: x.get("health_score") or 100)
    
    def get_engagement(self, engagement_id: str) -> Optional[dict]:
        """Get a single engagement by ID."""
        engagements = self._load_json("engagements.json")
        
        for eng in engagements:
            if eng.get("engagement_id") == engagement_id:
                return eng
        return None
    
    def get_engagement_with_details(self, engagement_id: str) -> Optional[dict]:
        """Get engagement with related tasks and notes."""
        engagement = self.get_engagement(engagement_id)
        if not engagement:
            return None
        
        # Add tasks
        all_tasks = self._load_json("tasks.json")
        engagement["tasks"] = [
            t for t in all_tasks if t.get("engagement_id") == engagement_id
        ]
        
        # Add notes
        all_notes = self._load_json("delivery_notes.json")
        engagement["notes"] = sorted(
            [n for n in all_notes if n.get("engagement_id") == engagement_id],
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        
        return engagement
    
    # ----- Tasks -----
    
    def get_tasks(self, engagement_id: Optional[str] = None) -> list:
        """Get tasks, optionally filtered by engagement."""
        tasks = self._load_json("tasks.json")
        
        if engagement_id:
            tasks = [t for t in tasks if t.get("engagement_id") == engagement_id]
        
        return tasks
    
    # ----- Delivery Notes -----
    
    def get_delivery_notes(self, engagement_id: Optional[str] = None, 
                           limit: int = 50) -> list:
        """Get delivery notes, optionally filtered by engagement."""
        notes = self._load_json("delivery_notes.json")
        
        if engagement_id:
            notes = [n for n in notes if n.get("engagement_id") == engagement_id]
        
        # Sort by date descending
        notes = sorted(notes, key=lambda x: x.get("created_at", ""), reverse=True)
        
        return notes[:limit]
    
    # ----- AI Insights -----
    
    def get_insights(self, engagement_id: Optional[str] = None,
                     insight_type: Optional[str] = None,
                     limit: int = 50) -> list:
        """Get stored AI insights."""
        insights = self._load_json("ai_insights.json")
        
        if engagement_id:
            insights = [i for i in insights if i.get("engagement_id") == engagement_id]
        
        if insight_type:
            insights = [i for i in insights if i.get("insight_type") == insight_type]
        
        # Sort by date descending
        insights = sorted(
            insights, 
            key=lambda x: x.get("generated_at", ""), 
            reverse=True
        )
        
        return insights[:limit]
    
    def save_insight(self, insight: dict):
        """Save a new AI insight."""
        insights = self._load_json("ai_insights.json")
        insights.append(insight)
        self._save_json("ai_insights.json", insights)
    
    # ----- Metrics -----
    
    def get_ai_metrics(self, days: int = 30) -> list:
        """Get AI tool usage metrics."""
        metrics = self._load_json("ai_metrics.json")
        return metrics
    
    def get_metrics_summary(self) -> dict:
        """Get aggregated metrics summary."""
        metrics = self._load_json("ai_metrics.json")
        insights = self._load_json("ai_insights.json")
        engagements = self._load_json("engagements.json")
        
        total_insights = sum(m.get("insights_generated", 0) for m in metrics)
        total_time_saved = sum(m.get("estimated_time_saved_minutes", 0) for m in metrics)
        
        # Group by role
        by_role = {}
        for m in metrics:
            role = m.get("role", "Unknown")
            if role not in by_role:
                by_role[role] = {"insights": 0, "time_saved": 0}
            by_role[role]["insights"] += m.get("insights_generated", 0)
            by_role[role]["time_saved"] += m.get("estimated_time_saved_minutes", 0)
        
        # Group by date
        by_date = {}
        for m in metrics:
            date = m.get("date", "")
            if date not in by_date:
                by_date[date] = 0
            by_date[date] += m.get("insights_generated", 0)
        
        return {
            "total_engagements": len(engagements),
            "active_engagements": len([e for e in engagements if e.get("status") == "Active"]),
            "at_risk_engagements": len([e for e in engagements if e.get("status") == "At Risk"]),
            "total_insights_generated": total_insights,
            "stored_insights": len(insights),
            "estimated_time_saved_minutes": total_time_saved,
            "estimated_time_saved_hours": round(total_time_saved / 60, 1),
            "by_role": by_role,
            "daily_trend": [
                {"date": k, "insights": v} 
                for k, v in sorted(by_date.items())[-30:]
            ]
        }
    
    # ----- Team -----
    
    def get_team_members(self) -> list:
        """Get all team members."""
        return self._load_json("team_members.json")
    
    # ----- Dashboard -----
    
    def get_dashboard_data(self) -> dict:
        """Get all data needed for the dashboard overview."""
        engagements = self.get_engagements()
        metrics = self.get_metrics_summary()
        
        # Calculate health distribution
        health_distribution = {
            "healthy": len([e for e in engagements if (e.get("health_score") or 0) >= 75]),
            "warning": len([e for e in engagements if 50 <= (e.get("health_score") or 0) < 75]),
            "critical": len([e for e in engagements if (e.get("health_score") or 0) < 50])
        }
        
        # Get recent insights
        recent_insights = self.get_insights(limit=5)
        
        return {
            "engagements": engagements,
            "health_distribution": health_distribution,
            "metrics": metrics,
            "recent_insights": recent_insights
        }


# Singleton instance
_connector: Optional[DatabricksConnector] = None


def get_connector() -> DatabricksConnector:
    """Get or create the connector singleton."""
    global _connector
    if _connector is None:
        _connector = DatabricksConnector()
    return _connector
