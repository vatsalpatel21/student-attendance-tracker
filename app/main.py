import sqlite3
import csv
import io
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
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
    conn.commit()
    conn.close()

init_db()

class AttendanceRecord(BaseModel):
    student_id: str
    student_name: str
    status: str
    date: Optional[str] = None  # Format: YYYY-MM-DD (optional, defaults to today)

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
        <!-- Header -->
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

        <!-- Form Card -->
        <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
            <h2 class="text-lg font-semibold text-slate-200 mb-4">Mark Attendance with Custom Date</h2>
            <form id="attendanceForm" class="grid grid-cols-1 md:grid-cols-5 gap-3">
                <input type="text" id="student_id" placeholder="Student ID (e.g., STU101)" required
                    class="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-400">
                <input type="text" id="student_name" placeholder="Student Name" required
                    class="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-400">
                <select id="status" class="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-400">
                    <option value="Present">Present</option>
                    <option value="Absent">Absent</option>
                </select>
                <input type="date" id="record_date"
                    class="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-400">
                <button type="submit" class="bg-emerald-500 hover:bg-emerald-600 font-semibold text-slate-950 px-4 py-2.5 rounded-lg text-sm transition shadow-lg shadow-emerald-500/20">
                    Record
                </button>
            </form>
        </div>

        <!-- Monthly Report Export Card -->
        <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
                <h2 class="text-lg font-semibold text-slate-200">Export Monthly Report</h2>
                <p class="text-xs text-slate-400">Select any month to download an official attendance spreadsheet</p>
            </div>
            <div class="flex items-center gap-3 w-full md:w-auto">
                <input type="month" id="report_month" value="2026-10"
                    class="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-400">
                <button onclick="downloadReport()" class="bg-indigo-600 hover:bg-indigo-700 text-white font-medium px-4 py-2 rounded-lg text-sm transition shadow-lg shadow-indigo-600/20 whitespace-nowrap">
                    Download CSV
                </button>
            </div>
        </div>

        <!-- Table Card -->
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
                            <th class="px-4 py-3">Date & Time</th>
                            <th class="px-4 py-3 text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody id="recordsBody" class="divide-y divide-slate-800"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // Set today as default date in form
        document.getElementById('record_date').value = new Date().toISOString().split('T')[0];

        async function loadRecords() {
            try {
                const res = await fetch('/api/attendance');
                const data = await res.json();
                const body = document.getElementById('recordsBody');
                body.innerHTML = '';
                if (data.length === 0) {
                    body.innerHTML = `
                        <tr>
                            <td colspan="6" class="px-4 py-8 text-center text-slate-500 text-sm">
                                No attendance records found. Add one using the form above.
                            </td>
                        </tr>
                    `;
                    return;
                }
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
                            <td class="px-4 py-3 text-right">
                                <button onclick="deleteRecord(${item.id})" class="text-xs text-rose-400 hover:text-rose-300 hover:underline">Delete</button>
                            </td>
                        </tr>
                    `;
                });
            } catch (err) {
                console.error('Error fetching records:', err);
            }
        }

        async function deleteRecord(id) {
            if (!confirm(`Delete record #${id}?`)) return;
            const res = await fetch(`/api/attendance/${id}`, { method: 'DELETE' });
            if (res.ok) loadRecords();
        }

        document.getElementById('attendanceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const record = {
                student_id: document.getElementById('student_id').value,
                student_name: document.getElementById('student_name').value,
                status: document.getElementById('status').value,
                date: document.getElementById('record_date').value
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

        function downloadReport() {
            const month = document.getElementById('report_month').value;
            if (!month) {
                alert('Please select a month (YYYY-MM)');
                return;
            }
            window.location.href = `/api/attendance/export/csv?month=${month}`;
        }

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
    # Use selected custom date or default to current date
    now = datetime.now()
    if record.date:
        timestamp_str = f"{record.date} {now.strftime('%H:%M:%S')}"
    else:
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO attendance (student_id, student_name, status, timestamp) VALUES (?, ?, ?, ?)",
        (record.student_id, record.student_name, record.status, timestamp_str)
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
            "timestamp": timestamp_str
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

@app.get("/api/attendance/export/csv")
def export_monthly_csv(month: str = "2026-10"):
    """
    Exports attendance records for a given month (format: YYYY-MM) as a CSV download.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, student_id, student_name, status, timestamp FROM attendance WHERE timestamp LIKE ? ORDER BY timestamp ASC",
        (f"{month}%",)
    )
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Student ID", "Student Name", "Status", "Timestamp"])
    for row in rows:
        writer.writerow([row["id"], row["student_id"], row["student_name"], row["status"], row["timestamp"]])

    output.seek(0)
    filename = f"attendance_report_{month}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
