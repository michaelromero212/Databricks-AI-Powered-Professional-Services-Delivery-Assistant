"""
Unit Tests for PS Delivery Assistant API

Tests cover core API endpoints and functionality.
Run with: pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app', 'backend'))


class TestHealthEndpoint:
    """Tests for the /api/health endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from api import app
        return TestClient(app)
    
    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get("/api/health")
        assert response.status_code == 200
    
    def test_health_returns_status(self, client):
        """Health endpoint should return status field."""
        response = client.get("/api/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_health_returns_timestamp(self, client):
        """Health endpoint should return timestamp."""
        response = client.get("/api/health")
        data = response.json()
        assert "timestamp" in data
    
    def test_health_returns_ai_connected(self, client):
        """Health endpoint should indicate AI connection status."""
        response = client.get("/api/health")
        data = response.json()
        assert "ai_connected" in data
        assert isinstance(data["ai_connected"], bool)


class TestDashboardEndpoint:
    """Tests for the /api/dashboard endpoint."""
    
    @pytest.fixture
    def client(self):
        from api import app
        return TestClient(app)
    
    def test_dashboard_returns_200(self, client):
        """Dashboard endpoint should return 200 OK."""
        response = client.get("/api/dashboard")
        assert response.status_code == 200
    
    def test_dashboard_contains_engagements(self, client):
        """Dashboard should return engagements list."""
        response = client.get("/api/dashboard")
        data = response.json()
        assert "engagements" in data
        assert isinstance(data["engagements"], list)
    
    def test_dashboard_contains_metrics(self, client):
        """Dashboard should return metrics."""
        response = client.get("/api/dashboard")
        data = response.json()
        assert "metrics" in data
    
    def test_dashboard_contains_health_distribution(self, client):
        """Dashboard should contain health distribution."""
        response = client.get("/api/dashboard")
        data = response.json()
        assert "health_distribution" in data


class TestEngagementsEndpoint:
    """Tests for engagement endpoints."""
    
    @pytest.fixture
    def client(self):
        from api import app
        return TestClient(app)
    
    def test_list_engagements_returns_200(self, client):
        """List engagements should return 200 OK."""
        response = client.get("/api/engagements")
        assert response.status_code == 200
    
    def test_list_engagements_returns_list(self, client):
        """List engagements should return a list."""
        response = client.get("/api/engagements")
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_engagements_filter_by_status(self, client):
        """Engagements can be filtered by status."""
        response = client.get("/api/engagements?status=Active")
        assert response.status_code == 200
    
    def test_get_engagement_not_found(self, client):
        """Getting non-existent engagement returns 404."""
        response = client.get("/api/engagements/nonexistent-id")
        assert response.status_code == 404


class TestNotebooksEndpoint:
    """Tests for Databricks notebook endpoints."""
    
    @pytest.fixture
    def client(self):
        from api import app
        return TestClient(app)
    
    def test_list_notebooks_returns_200(self, client):
        """List notebooks should return 200 OK."""
        response = client.get("/api/notebooks")
        assert response.status_code == 200
    
    def test_list_notebooks_contains_list(self, client):
        """List notebooks should contain notebooks array."""
        response = client.get("/api/notebooks")
        data = response.json()
        assert "notebooks" in data
        assert isinstance(data["notebooks"], list)
    
    def test_list_notebooks_has_correct_count(self, client):
        """Should have 4 configured notebooks."""
        response = client.get("/api/notebooks")
        data = response.json()
        assert len(data["notebooks"]) == 4


class TestDataRegeneration:
    """Tests for data management endpoints."""
    
    @pytest.fixture
    def client(self):
        from api import app
        return TestClient(app)
    
    def test_regenerate_data_returns_200(self, client):
        """Regenerate data should return 200 OK."""
        response = client.post("/api/data/regenerate")
        assert response.status_code == 200
    
    def test_regenerate_data_returns_success(self, client):
        """Regenerate data should indicate success."""
        response = client.post("/api/data/regenerate")
        data = response.json()
        assert data.get("success") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
