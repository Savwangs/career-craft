import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from main import app
import json
import os
from dotenv import load_dotenv

load_dotenv()

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost/test_resume_manager"
)
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)
    # Provide the db session to the test
    db = TestingSessionLocal()
    yield db  # This will be injected into the test
    # After the test, drop all tables to clean up
    Base.metadata.drop_all(bind=engine)
    db.close()

def test_create_user(test_db):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    print(f"Response: {response.json()}")  # Log the response body to understand the error
    assert response.status_code == 200
    assert "access_token" in response.json()
    return response.json()["access_token"]

def test_create_resume(test_db):
    # First create a user
    token = test_create_user(test_db)  # pass test_db here
    
    resume_data = {
        "content": json.dumps({
            "personal_info": {
                "name": "Test User",
                "email": "test@example.com"
            }
        })
    }
    
    response = client.post(
        "/resumes/",
        json=resume_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert "id" in response.json()
    return response.json()["id"], token

def test_get_resume(test_db):
    # Create a resume first
    resume_id, token = test_create_resume()
    
    response = client.get(
        f"/resumes/{resume_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == resume_id

def test_update_resume(test_db):
    # Create a resume first
    resume_id, token = test_create_resume()
    
    update_data = {
        "content": json.dumps({
            "personal_info": {
                "name": "Updated Test User",
                "email": "test@example.com"
            }
        })
    }
    
    response = client.put(
        f"/resumes/{resume_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert "Updated Test User" in response.json()["content"]

def test_delete_resume(test_db):
    # Create a resume first
    resume_id, token = test_create_resume()
    
    response = client.delete(
        f"/resumes/{resume_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 204
    
    # Verify it's deleted
    response = client.get(
        f"/resumes/{resume_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

def test_list_resumes(test_db):
    # Create a resume first
    _, token = test_create_resume()
    
    response = client.get(
        "/resumes/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0