import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import get_db, Base
from main import app
import tempfile
import os

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture
def test_user():
    """Create a test user and return login token"""
    user_data = {
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
        "role": "reporter"
    }
    
    # Register user
    response = client.post("/users/register", json=user_data)
    assert response.status_code == 200
    
    # Login to get token
    login_data = {"username": "test@example.com", "password": "testpass123"}
    response = client.post("/users/token", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"token": token, "user": user_data}

@pytest.fixture
def admin_user():
    """Create an admin user and return login token"""
    user_data = {
        "email": "admin@example.com",
        "password": "adminpass123",
        "full_name": "Admin User",
        "role": "admin"
    }
    
    # Register user
    response = client.post("/users/register", json=user_data)
    assert response.status_code == 200
    
    # Login to get token
    login_data = {"username": "admin@example.com", "password": "adminpass123"}
    response = client.post("/users/token", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"token": token, "user": user_data}

class TestAuthentication:
    """Test authentication and authorization"""
    
    def test_register_user(self):
        """Test user registration"""
        response = client.post("/users/register", json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
            "role": "reporter"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data
    
    def test_login(self):
        """Test user login"""
        # First register a user
        client.post("/users/register", json={
            "email": "logintest@example.com",
            "password": "password123",
            "full_name": "Login Test"
        })
        
        # Then login
        response = client.post("/users/token", data={
            "username": "logintest@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = client.post("/users/token", data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

class TestIssues:
    """Test issue management"""
    
    def test_create_issue(self, test_user):
        """Test creating an issue"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        # Create test file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
            tmp_file.write(b"Test file content")
            tmp_file_path = tmp_file.name
        
        try:
            with open(tmp_file_path, "rb") as f:
                response = client.post(
                    "/issues/",
                    headers=headers,
                    data={
                        "title": "Test Issue",
                        "description": "This is a test issue",
                        "severity": "medium"
                    },
                    files={"file": ("test.txt", f, "text/plain")}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Test Issue"
            assert data["severity"] == "medium"
            assert "id" in data
        finally:
            os.unlink(tmp_file_path)
    
    def test_get_issues(self, test_user):
        """Test getting issues list"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        response = client.get("/issues/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_dashboard_stats(self, test_user):
        """Test getting dashboard statistics"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        response = client.get("/issues/dashboard/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_issues" in data
        assert "severity_breakdown" in data
        assert "status_breakdown" in data
    
    def test_unauthorized_access(self):
        """Test accessing issues without authentication"""
        response = client.get("/issues/")
        assert response.status_code == 401

class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def test_reporter_cannot_delete_issue(self, test_user):
        """Test that reporters cannot delete issues"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        
        # Create an issue first
        response = client.post(
            "/issues/",
            headers=headers,
            data={
                "title": "Test Issue for Deletion",
                "description": "This issue will be deleted",
                "severity": "low"
            }
        )
        assert response.status_code == 200
        issue_id = response.json()["id"]
        
        # Try to delete (should fail)
        response = client.delete(f"/issues/{issue_id}", headers=headers)
        assert response.status_code == 403
    
    def test_admin_can_delete_issue(self, admin_user):
        """Test that admins can delete issues"""
        headers = {"Authorization": f"Bearer {admin_user['token']}"}
        
        # Create an issue first
        response = client.post(
            "/issues/",
            headers=headers,
            data={
                "title": "Admin Test Issue",
                "description": "This issue will be deleted by admin",
                "severity": "high"
            }
        )
        assert response.status_code == 200
        issue_id = response.json()["id"]
        
        # Delete the issue (should succeed)
        response = client.delete(f"/issues/{issue_id}", headers=headers)
        assert response.status_code == 200

class TestAPI:
    """Test general API functionality"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_openapi_docs(self):
        """Test OpenAPI documentation endpoints"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data

if __name__ == "__main__":
    pytest.main([__file__])
