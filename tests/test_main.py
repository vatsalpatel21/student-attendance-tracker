import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    init_db()
    yield
    # Cleanup DB after testing runs
    if os.path.exists("attendance.db"):
        os.remove("attendance.db")

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}

def test_record_attendance_and_fetch():
    payload = {
        "student_id": "ST101",
        "student_name": "Akil Surti",
        "course_code": "CS402",
        "status": "Present"
    }
    # 1. Post record
    post_res = client.post("/attendance", json=payload)
    assert post_res.status_code == 201
    assert post_res.json()["data"]["student_id"] == "ST101"

    # 2. Get student records
    get_res = client.get("/attendance/ST101")
    assert get_res.status_code == 200
    records = get_res.json()
    assert len(records) >= 1
    assert records[0]["status"] == "Present"

def test_student_not_found():
    res = client.get("/attendance/UNKNOWN999")
    assert res.status_code == 404