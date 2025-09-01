import pytest
from fastapi import status

class TestGeneralEndpoints:
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "Welcome to Eko Backend API" in data["message"]
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_api_docs_available(self, client):
        """Test that API documentation is available."""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
    
    def test_openapi_schema_available(self, client):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data 