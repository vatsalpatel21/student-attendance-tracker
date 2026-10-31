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
    assert response.json()["status"] == "healthy"

def test_get_attendance():
    response = client.get("/api/attendance")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_post_attendance_with_custom_date():
    payload = {
        "student_id": "TEST_DATE",
        "student_name": "Date Tester",
        "status": "Present",
        "date": "2026-10-15"
    }
    response = client.post("/api/attendance", json=payload)
    assert response.status_code == 201
    assert "2026-10-15" in response.json()["record"]["timestamp"]

def test_export_monthly_csv():
    response = client.get("/api/attendance/export/csv?month=2026-10")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Student ID" in response.text
