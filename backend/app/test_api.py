"""
Tests for Iris Data API
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app
from app.config import settings

# Create test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_check(self):
        """Test basic health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_detailed_health_check(self):
        """Test detailed health check"""
        response = client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "system" in data
        assert "configuration" in data


class TestDataEndpoints:
    """Test data endpoints"""
    
    def test_get_species_data_setosa(self):
        """Test getting setosa data"""
        response = client.get("/api/data/setosa")
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "setosa"
        assert data["count"] > 0
        assert len(data["sepal_length"]) == data["count"]
    
    def test_get_species_data_virginica(self):
        """Test getting virginica data"""
        response = client.get("/api/data/virginica")
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "virginica"
        assert data["count"] > 0
    
    def test_get_invalid_species(self):
        """Test getting invalid species"""
        response = client.get("/api/data/invalid_species")
        assert response.status_code == 404
    
    def test_get_data_summary(self):
        """Test getting data summary"""
        response = client.get("/api/data")
        assert response.status_code == 200
        data = response.json()
        assert "total_records" in data
        assert "species_count" in data
        assert "statistics" in data
    
    def test_list_species(self):
        """Test listing species"""
        response = client.get("/api/data/species/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


class TestDataTransformations:
    """Test data transformation features"""
    
    def test_normalized_data(self):
        """Test data normalization"""
        response = client.get("/api/data/setosa?normalize=true")
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "setosa"
        # Check that normalized columns exist
        assert "metadata" in data
    
    def test_outlier_removal(self):
        """Test outlier removal"""
        response = client.get("/api/data/setosa?remove_outliers=true")
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "setosa"
        assert data["count"] >= 0  # May have fewer records after outlier removal


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


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])