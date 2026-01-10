"""
Unit Tests for AI Client

Tests cover prompt formatting and error handling.
Run with: pytest tests/ -v
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app', 'backend'))


class TestAIClientInitialization:
    """Tests for AI client initialization."""
    
    @pytest.mark.skip(reason="Environment-dependent: requires HF token to be unset")
    def test_client_requires_token(self):
        """Client should raise error without token."""
        import importlib
        import ai_client
        
        # Temporarily unset token
        original = os.environ.get("HUGGINGFACE_API_TOKEN")
        if original:
            del os.environ["HUGGINGFACE_API_TOKEN"]
        
        try:
            # Reload the module to clear any cached client
            importlib.reload(ai_client)
            from ai_client import AIClient
            with pytest.raises(ValueError):
                AIClient(api_token=None)
        except ValueError:
            # Expected - token required
            pass
        finally:
            if original:
                os.environ["HUGGINGFACE_API_TOKEN"] = original
                importlib.reload(ai_client)
    
    def test_client_validates_token_length(self):
        """Client should reject too-short tokens."""
        from ai_client import AIClient
        with pytest.raises(ValueError, match="Invalid API token"):
            AIClient(api_token="short")


class TestPromptTemplates:
    """Tests for prompt template formatting."""
    
    def test_all_prompt_types_exist(self):
        """Should have templates for all insight types."""
        from ai_client import AIClient
        
        expected_types = [
            "health_summary",
            "risk_detection",
            "theme_extraction",
            "action_recommendation"
        ]
        
        for insight_type in expected_types:
            assert insight_type in AIClient.PROMPT_TEMPLATES
    
    def test_health_summary_template_has_placeholders(self):
        """Health summary template should have key placeholders."""
        from ai_client import AIClient
        
        template = AIClient.PROMPT_TEMPLATES["health_summary"]
        assert "{customer_name}" in template
        assert "{health_score}" in template
        assert "{status}" in template


class TestInsightGeneration:
    """Tests for insight generation with mocked LLM."""
    
    @pytest.fixture
    def mock_client(self):
        """Create AI client with mocked inference."""
        with patch.dict(os.environ, {"HUGGINGFACE_API_TOKEN": "test_token_valid_length"}):
            with patch("ai_client.InferenceClient") as mock_inference:
                # Mock the chat completion response
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = "Test insight response"
                mock_inference.return_value.chat_completion.return_value = mock_response
                
                from ai_client import AIClient
                client = AIClient(api_token="test_token_valid_length")
                return client
    
    def test_generate_insight_returns_dict(self, mock_client):
        """Generate insight should return a dictionary."""
        result = mock_client.generate_insight(
            "health_summary",
            {"customer_name": "Test Corp", "status": "Active"}
        )
        assert isinstance(result, dict)
    
    def test_generate_insight_has_required_fields(self, mock_client):
        """Generated insight should have required fields."""
        result = mock_client.generate_insight(
            "health_summary",
            {"customer_name": "Test Corp"}
        )
        assert "success" in result
        assert "insight_type" in result
        assert "generated_at" in result
    
    def test_generate_insight_unknown_type_fails(self, mock_client):
        """Unknown insight type should fail gracefully."""
        result = mock_client.generate_insight(
            "unknown_type",
            {"customer_name": "Test Corp"}
        )
        assert result["success"] is False
        assert "error" in result
    
    def test_generate_full_analysis_returns_list(self, mock_client):
        """Full analysis should return list of insights."""
        result = mock_client.generate_full_analysis(
            {"customer_name": "Test Corp"}
        )
        assert isinstance(result, list)
        assert len(result) == 4  # 4 insight types


class TestConnectionCheck:
    """Tests for connection checking."""
    
    @pytest.fixture
    def mock_client(self):
        """Create AI client with mocked inference."""
        with patch.dict(os.environ, {"HUGGINGFACE_API_TOKEN": "test_token_valid_length"}):
            with patch("ai_client.InferenceClient") as mock_inference:
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = "Hi"
                mock_inference.return_value.chat_completion.return_value = mock_response
                
                from ai_client import AIClient
                client = AIClient(api_token="test_token_valid_length")
                return client
    
    def test_check_connection_returns_dict(self, mock_client):
        """Check connection should return status dict."""
        result = mock_client.check_connection()
        assert isinstance(result, dict)
        assert "connected" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
