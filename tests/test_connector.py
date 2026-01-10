"""
Unit Tests for Databricks Connector

Tests cover data loading and caching.
Run with: pytest tests/ -v
"""

import pytest
import json
import tempfile
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app', 'backend'))


class TestDatabricksConnectorInit:
    """Tests for connector initialization."""
    
    def test_defaults_to_local_mode(self):
        """Connector should default to local mode."""
        from databricks_connector import DatabricksConnector
        connector = DatabricksConnector()
        assert connector.mode == "local"
    
    def test_can_specify_mode(self):
        """Connector should accept mode parameter."""
        from databricks_connector import DatabricksConnector
        connector = DatabricksConnector(mode="local")
        assert connector.mode == "local"


class TestLocalDataLoading:
    """Tests for loading local JSON data."""
    
    @pytest.fixture
    def connector(self):
        """Create local mode connector."""
        from databricks_connector import DatabricksConnector
        return DatabricksConnector(mode="local")
    
    def test_get_engagements_returns_list(self, connector):
        """Get engagements should return a list."""
        result = connector.get_engagements()
        assert isinstance(result, list)
    
    def test_get_engagements_can_filter_by_status(self, connector):
        """Engagements can be filtered by status."""
        all_engagements = connector.get_engagements()
        active = connector.get_engagements(status="Active")
        
        # Filtered should be subset
        assert len(active) <= len(all_engagements)
    
    def test_get_tasks_returns_list(self, connector):
        """Get tasks should return a list."""
        result = connector.get_tasks()
        assert isinstance(result, list)
    
    def test_get_delivery_notes_returns_list(self, connector):
        """Get delivery notes should return a list."""
        result = connector.get_delivery_notes()
        assert isinstance(result, list)
    
    def test_get_delivery_notes_respects_limit(self, connector):
        """Delivery notes should respect limit parameter."""
        result = connector.get_delivery_notes(limit=5)
        assert len(result) <= 5


class TestEngagementLookup:
    """Tests for single engagement retrieval."""
    
    @pytest.fixture
    def connector(self):
        from databricks_connector import DatabricksConnector
        return DatabricksConnector(mode="local")
    
    def test_get_engagement_returns_none_for_invalid_id(self, connector):
        """Getting non-existent engagement returns None."""
        result = connector.get_engagement("invalid-id-12345")
        assert result is None
    
    def test_get_engagement_with_details_returns_dict(self, connector):
        """Get engagement with details should return dict."""
        engagements = connector.get_engagements()
        if engagements:
            engagement_id = engagements[0]["engagement_id"]
            result = connector.get_engagement_with_details(engagement_id)
            assert isinstance(result, dict)
            # Result contains engagement data plus tasks and notes
            assert "customer_name" in result or "engagement" in result


class TestDashboardData:
    """Tests for dashboard data aggregation."""
    
    @pytest.fixture
    def connector(self):
        from databricks_connector import DatabricksConnector
        return DatabricksConnector(mode="local")
    
    def test_get_dashboard_data_returns_dict(self, connector):
        """Dashboard data should return dictionary."""
        result = connector.get_dashboard_data()
        assert isinstance(result, dict)
    
    def test_dashboard_data_has_required_keys(self, connector):
        """Dashboard data should have all required keys."""
        result = connector.get_dashboard_data()
        required_keys = ["engagements", "metrics", "health_distribution"]
        for key in required_keys:
            assert key in result


class TestMetrics:
    """Tests for metrics retrieval."""
    
    @pytest.fixture
    def connector(self):
        from databricks_connector import DatabricksConnector
        return DatabricksConnector(mode="local")
    
    def test_get_ai_metrics_returns_list(self, connector):
        """Get AI metrics should return list."""
        result = connector.get_ai_metrics()
        assert isinstance(result, list)
    
    def test_get_metrics_summary_returns_dict(self, connector):
        """Metrics summary should return dictionary."""
        result = connector.get_metrics_summary()
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
