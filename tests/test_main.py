from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "Student Attendance Tracker" in response.text

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "student-attendance-tracker",
        "database": "sqlite3"
    }

def test_get_attendance():
    response = client.get("/api/attendance")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_post_attendance():
    payload = {
        "student_id": "TEST999",
        "student_name": "Integration Test",
        "status": "Present"
    }
    response = client.post("/api/attendance", json=payload)
    assert response.status_code == 201
    assert response.json()["message"] == "Attendance recorded successfully in SQL database"
