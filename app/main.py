import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

app = FastAPI(title="Student Attendance Tracker", version="1.0.0")
DB_NAME = "attendance.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            status TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM attendance")
    if cursor.fetchone()[0] == 0:
        default_records = [
            ("STU101", "Aarav Sharma", "Present", "2026-10-30 09:00:00"),
            ("STU102", "Diya Patel", "Present", "2026-10-30 09:05:00"),
            ("STU103", "Rohan Mehta", "Absent", "2026-10-30 09:10:00")
        ]
        cursor.executemany(
            "INSERT INTO attendance (student_id, student_name, status, timestamp) VALUES (?, ?, ?, ?)",
            default_records
        )
        conn.commit()
    conn.close()

init_db()

class AttendanceRecord(BaseModel):
    student_id: str
    student_name: str
    status: str

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Attendance Tracker</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-4 md:p-8 font-sans">
    <div class="max-w-4xl mx-auto space-y-6">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
            <div>
                <h1 class="text-3xl font-extrabold tracking-tight text-emerald-400">Student Attendance Tracker</h1>
                <p class="text-slate-400 text-sm mt-1">DevOps CI/CD Pipeline | SQLite Engine | Autonomous Deployment</p>
            </div>
            <div class="mt-4 md:mt-0 flex gap-2">
                <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Live Render
                </span>
                <a href="/docs" target="_blank" class="px-3 py-1 rounded-full text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition">
                    Swagger API Docs &rarr;
                </a>
            </div>
        </div>

        <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
            <h2 class="text-lg font-semibold text-slate-200 mb-4">Mark New Attendance</h2>
            <form id="attendanceForm" class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <input type="text" id="student_id" placeholder="Student ID (e.g., STU104)" required
                    class="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-400">
                <input type="text" id="student_name" placeholder="Student Name" required
                    class="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-400">
                <select id="status" class="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-400">
                    <option value="Present">Present</option>
                    <option value="Absent">Absent</option>
                </select>
                <button type="submit" class="bg-emerald-500 hover:bg-emerald-600 font-semibold text-slate-950 px-4 py-2.5 rounded-lg text-sm transition shadow-lg shadow-emerald-500/20">
                    Record Attendance
                </button>
            </form>
        </div>

        <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl overflow-hidden">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-lg font-semibold text-slate-200">SQL Attendance Records</h2>
                <button onclick="loadRecords()" class="text-xs text-emerald-400 hover:underline">Refresh List</button>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm">
                    <thead class="text-xs uppercase bg-slate-800/60 text-slate-400 border-b border-slate-800">
                        <tr>
                            <th class="px-4 py-3">SQL ID</th>
                            <th class="px-4 py-3">Student ID</th>
                            <th class="px-4 py-3">Name</th>
                            <th class="px-4 py-3">Status</th>
                            <th class="px-4 py-3">Timestamp</th>
                        </tr>
                    </thead>
                    <tbody id="recordsBody" class="divide-y divide-slate-800"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        async function loadRecords() {
            try {
                const res = await fetch('/api/attendance');
                const data = await res.json();
                const body = document.getElementById('recordsBody');
                body.innerHTML = '';
                data.forEach(item => {
                    const isPresent = item.status === 'Present';
                    const badgeClass = isPresent ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20';
                    body.innerHTML += `
                        <tr class="hover:bg-slate-800/40 transition">
                            <td class="px-4 py-3 font-mono text-slate-500 text-xs">${item.id}</td>
                            <td class="px-4 py-3 font-mono text-slate-300">${item.student_id}</td>
                            <td class="px-4 py-3 font-medium text-white">${item.student_name}</td>
                            <td class="px-4 py-3">
                                <span class="inline-flex px-2 py-0.5 rounded text-xs font-semibold border ${badgeClass}">
                                    ${item.status}
                                </span>
                            </td>
                            <td class="px-4 py-3 text-slate-400 font-mono text-xs">${item.timestamp}</td>
                        </tr>
                    `;
                });
            } catch (err) {
                console.error('Error fetching records:', err);
            }
        }

        document.getElementById('attendanceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const record = {
                student_id: document.getElementById('student_id').value,
                student_name: document.getElementById('student_name').value,
                status: document.getElementById('status').value
            };
            const res = await fetch('/api/attendance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(record)
            });
            if (res.ok) {
                document.getElementById('student_id').value = '';
                document.getElementById('student_name').value = '';
                loadRecords();
            } else {
                alert('Failed to record attendance');
            }
        });

        loadRecords();
    </script>
</body>
</html>"""

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "student-attendance-tracker", "database": "sqlite3"}

@app.get("/api/attendance", response_model=List[Dict])
def get_attendance():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, student_id, student_name, status, timestamp FROM attendance ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/attendance", status_code=201)
def add_attendance(record: AttendanceRecord):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO attendance (student_id, student_name, status, timestamp) VALUES (?, ?, ?, ?)",
        (record.student_id, record.student_name, record.status, now)
    )
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return {
        "message": "Attendance recorded successfully in SQL database",
        "record": {
            "id": inserted_id,
            "student_id": record.student_id,
            "student_name": record.student_name,
            "status": record.status,
            "timestamp": now
        }
    }

@app.delete("/api/attendance/{record_id}")
def delete_attendance(record_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE id = ?", (record_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"Record with ID {record_id} not found")
    return {"message": f"Record {record_id} deleted successfully"}
