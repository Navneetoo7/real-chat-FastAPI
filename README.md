What is implemented

Auth: Email/password sign-up and login with JWT access + refresh tokens; passwords hashed with Argon2
Conversations: REST CRUD (create, list, rename, delete) and paginated message history
Real-time messaging: WebSocket endpoint per conversation; messages persisted to PostgreSQL and broadcast to connected clients
Mock AI: Echo-based assistant reply over WebSocket
Redis pub/sub: Cross-instance fan-out for horizontal scaling (supports 2+ API replicas via Docker Compose profile)
Infrastructure: Docker Compose (Postgres, Redis, API), Alembic migrations, async FastAPI + SQLModel


How to run

git clone https://github.com/Navneetoo7/real-chat-FastAPI.git
cd real-chat-FastAPI
cp .env.example .env
docker compose up -d postgres redis
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
API docs: http://localhost:8000/docs

