from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
from app.database import get_connection, init_db

app = FastAPI(
    title="Student Attendance Tracker",
    description="DevOps Microservice with Autonomous CI/CD",
    version="1.0.0"
)

# Initialize database schema on startup
@app.on_event("startup")
def startup_event():
    init_db()

class AttendanceRecord(BaseModel):
    student_id: str
    student_name: str
    course_code: str
    status: Literal["Present", "Absent", "Late"]

@app.get("/")
def root():
    return {
        "service": "Student Attendance Tracker",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/attendance", status_code=201)
def mark_attendance(record: AttendanceRecord):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO attendance (student_id, student_name, course_code, status)
        VALUES (?, ?, ?, ?)
        """,
        (record.student_id, record.student_name, record.course_code, record.status)
    )
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return {"message": "Attendance recorded", "id": record_id, "data": record.model_dump()}

@app.get("/attendance/{student_id}")
def get_student_attendance(student_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, student_id, student_name, course_code, status, timestamp FROM attendance WHERE student_id = ?",
        (student_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        raise HTTPException(status_code=404, detail="No attendance records found for this student")
    
    return [dict(row) for row in rows]

@app.get("/attendance/summary/{course_code}")
def get_course_summary(course_code: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT status, COUNT(*) as count 
        FROM attendance 
        WHERE course_code = ? 
        GROUP BY status
        """,
        (course_code,)
    )
    rows = cursor.fetchall()
    conn.close()
    return {row["status"]: row["count"] for row in rows}