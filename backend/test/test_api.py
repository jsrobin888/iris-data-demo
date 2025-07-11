"""
Comprehensive test suite for Iris Data API
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app
from app.config import settings

# Create test client
client = TestClient(app)

# Test credentials
TEST_USERS = {
    "setosa": {
        "email": "setosa@example.com",
        "password": "password123"
    },
    "virginica": {
        "email": "virginica@example.com",
        "password": "password123"
    },
    "admin": {
        "email": "admin@example.com",
        "password": "admin123"
    }
}


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_check(self):
        """Test basic health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "data_loaded" in data
    
    def test_detailed_health_check(self):
        """Test detailed health check"""
        response = client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "system" in data
        assert "configuration" in data
        assert "data_info" in data


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_register_new_user(self):
        """Test user registration"""
        new_user = {
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User",
            "access_level": "setosa"
        }
        
        response = client.post("/api/v1/auth/register", json=new_user)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == new_user["email"]
        assert data["full_name"] == new_user["full_name"]
        assert data["access_level"] == new_user["access_level"]
        assert "password" not in data
    
    def test_register_duplicate_user(self):
        """Test registering duplicate user"""
        existing_user = {
            "email": "setosa@example.com",
            "password": "newpass123"
        }
        
        response = client.post("/api/v1/auth/register", json=existing_user)
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    def test_login_valid_credentials(self):
        """Test login with valid credentials"""
        response = client.post(
            "/api/v1/auth/login",
            json=TEST_USERS["setosa"]
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "wrong@example.com", "password": "wrongpass"}
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_get_current_user(self):
        """Test getting current user info"""
        # First login
        login_response = client.post(
            "/api/v1/auth/login",
            json=TEST_USERS["setosa"]
        )
        token = login_response.json()["access_token"]
        
        # Get user info
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_USERS["setosa"]["email"]
        assert data["access_level"] == "setosa"
    
    def test_refresh_token(self):
        """Test token refresh"""
        # Login to get tokens
        login_response = client.post(
            "/api/v1/auth/login",
            json=TEST_USERS["setosa"]
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data


class TestDataEndpoints:
    """Test data endpoints with access control"""
    
    def get_auth_headers(self, user_type="setosa"):
        """Helper to get auth headers"""
        login_response = client.post(
            "/api/v1/auth/login",
            json=TEST_USERS[user_type]
        )
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_data_summary_setosa_user(self):
        """Test data summary for setosa user"""
        headers = self.get_auth_headers("setosa")
        
        response = client.get("/api/v1/data/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_access_level"] == "setosa"
        assert data["accessible_species"] == ["setosa"]
        assert "setosa" in data["species_count"]
    
    def test_get_data_summary_admin_user(self):
        """Test data summary for admin user"""
        headers = self.get_auth_headers("admin")
        
        response = client.get("/api/v1/data/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_access_level"] == "all"
        assert len(data["accessible_species"]) >= 3  # All species
    
    def test_list_accessible_species(self):
        """Test listing accessible species"""
        # Test setosa user
        headers = self.get_auth_headers("setosa")
        response = client.get("/api/v1/data/species/list", headers=headers)
        assert response.status_code == 200
        assert response.json() == ["setosa"]
        
        # Test admin user
        headers = self.get_auth_headers("admin")
        response = client.get("/api/v1/data/species/list", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) >= 3
    
    def test_get_species_data_with_access(self):
        """Test getting species data with proper access"""
        headers = self.get_auth_headers("setosa")
        
        response = client.get("/api/v1/data/species/setosa", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "setosa"
        assert data["count"] > 0
        assert len(data["sepal_length"]) == data["count"]
        assert "user_access_level" in data["metadata"]
    
    def test_get_species_data_without_access(self):
        """Test getting species data without access"""
        headers = self.get_auth_headers("setosa")
        
        response = client.get("/api/v1/data/species/virginica", headers=headers)
        assert response.status_code == 403
        assert "don't have access" in response.json()["detail"]
    
    def test_get_species_data_admin_access(self):
        """Test admin can access all species"""
        headers = self.get_auth_headers("admin")
        
        for species in ["setosa", "virginica", "versicolor"]:
            response = client.get(f"/api/v1/data/species/{species}", headers=headers)
            assert response.status_code == 200
            assert response.json()["species"] == species
    
    def test_get_my_data(self):
        """Test getting user's own species data"""
        headers = self.get_auth_headers("virginica")
        
        response = client.get("/api/v1/data/my-data", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "virginica"
    
    def test_data_transformations(self):
        """Test data transformation options"""
        headers = self.get_auth_headers("setosa")
        
        # Test normalization
        response = client.get(
            "/api/v1/data/species/setosa?normalize=true",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["transformations"]["normalized"] is True
        
        # Test outlier removal
        response = client.get(
            "/api/v1/data/species/setosa?remove_outliers=true",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["transformations"]["outliers_removed"] is True
    
    def test_data_pagination(self):
        """Test data pagination"""
        headers = self.get_auth_headers("setosa")
        
        # Test with limit
        response = client.get(
            "/api/v1/data/species/setosa?limit=5",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] <= 5
        
        # Test with limit and offset
        response = client.get(
            "/api/v1/data/species/setosa?limit=5&offset=2",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] <= 5
    
    def test_get_statistics(self):
        """Test getting statistics"""
        headers = self.get_auth_headers("setosa")
        
        response = client.get("/api/v1/data/statistics", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "setosa" in data
        assert "sepal_length" in data["setosa"]


class TestErrorHandling:
    """Test error handling"""
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoint without auth"""
        response = client.get("/api/v1/data/")
        assert response.status_code == 401
    
    def test_invalid_species(self):
        """Test requesting invalid species"""
        headers = TestDataEndpoints().get_auth_headers("admin")
        
        response = client.get(
            "/api/v1/data/species/invalid_species",
            headers=headers
        )
        assert response.status_code == 400
        assert "Invalid species" in response.json()["detail"]
    
    def test_malformed_token(self):
        """Test with malformed token"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get("/api/v1/data/", headers=headers)
        assert response.status_code == 401


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["name"] == settings.app_name


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])