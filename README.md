# Student Attendance Tracker (Autonomous CI/CD)

A lightweight REST API microservice built using FastAPI and containerized with Docker, featuring an automated end-to-end CI/CD pipeline using GitHub Actions and GitHub Container Registry (GHCR).

---

## Architecture & DevOps Flow

```text
Developer Git Push (main branch)
       │
       ▼
GitHub Actions CI
  ├── 1. Install dependencies & configure Python
  └── 2. Run unit tests via pytest
       │
       ▼
GitHub Actions CD (Autonomous)
  ├── 3. Build multi-stage Docker image
  ├── 4. Push image to GitHub Container Registry (GHCR)
  └── 5. Trigger live production webhook (Zero manual clicks)
```

---

## Tech Stack
* **Language/Framework:** Python 3.11, FastAPI, Pydantic
* **Database:** SQLite
* **Testing:** Pytest, HTTPX
* **Containerization:** Docker (Multi-stage build)
* **CI/CD:** GitHub Actions
* **Image Registry:** GitHub Container Registry (`ghcr.io`)

---

## Local Setup & Execution

### 1. Run with Python directly
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Run with Docker
```bash
# Build Docker image
docker build -t attendance-tracker:latest .

# Run container
docker run -p 8000:8000 attendance-tracker:latest
```

The service will run locally at `http://127.0.0.1:8000`.

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | System health and API version |
| `GET` | `/health` | Healthcheck endpoint |
| `POST` | `/attendance` | Log student attendance |
| `GET` | `/attendance/{student_id}` | Retrieve records by student ID |
| `GET` | `/attendance/summary/{course_code}` | Course attendance breakdown |

---

## Running Automated Tests
```bash
pytest tests/
```
## Live Deployment
- Production URL: https://student-attendance-tracker-j0gg.onrender.com
