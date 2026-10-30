# Stage 1: Build Dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final Runtime
FROM python:3.11-slim AS runner
WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /install /usr/local
COPY app/ ./app

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]