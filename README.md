# Campus Booking System – Backend API

A backend service for a multi-user campus room booking platform, built with **FastAPI**, **SQLAlchemy 2.0**, **Alembic**, and **JWT-based authentication**.

This project demonstrates structured backend architecture, stateless authentication, role-based access control (RBAC), and version-controlled database migrations.

---

## Overview

The system simulates a campus room booking backend that supports multiple user roles, secure authentication, and clear domain modeling.

**Core capabilities:**
- JWT authentication via OAuth2 password flow
- Role-based access control (`STUDENT` / `STAFF` / `ADMIN`)
- SQLAlchemy 2.0 ORM with Alembic migration management
- Dependency-injected database sessions
- Interactive Swagger documentation at `/docs`
- Layered application architecture with clean separation of concerns

---

## Architecture

The application follows a layered directory structure:

```
app/
├── api/        # Route handlers
├── core/       # Configuration and security utilities
├── db/         # Database engine and session management
├── models/     # SQLAlchemy ORM models
└── schemas/    # Pydantic request and response models
```

**Design principles:**
- Explicit dependency injection throughout
- Stateless JWT authentication — no server-side session state
- Clean separation between the transport layer and domain logic
- Version-controlled schema migrations via Alembic
- Conventional commit structure for a clear Git history

---

## Authentication & Authorization

Authentication uses the **OAuth2 password flow** with JWT bearer tokens.

**Flow:**
1. Register via `POST /auth/register`
2. Log in via `POST /auth/login` — receives an `access_token`
3. Include the token in subsequent requests:
   ```
   Authorization: Bearer <access_token>
   ```
4. The token is validated and the user resolved via the `get_current_user` dependency

**Role-based authorization** is enforced at the route level using reusable dependency guards:

```python
require_roles("ADMIN")
```

### Roles

| Role | Permissions |
|---|---|
| `STUDENT` | Create and view bookings |
| `STAFF` | Manage rooms and approve bookings |
| `ADMIN` | Full system control |

---

## Database

The system uses **SQLAlchemy 2.0** ORM with **Alembic** for migration management. Development runs on **SQLite**, and the configuration is **PostgreSQL-ready** for production deployment.

Migrations keep the schema version-controlled and reproducible across environments.

---

## Running Locally

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
alembic upgrade head

# 4. Start the development server
uvicorn app.main:app --reload
```

API documentation is available at: **http://127.0.0.1:8000/docs**

---

## Example Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Authenticate and receive a token |
| `GET` | `/auth/me` | Get the current authenticated user |

---

## Tech Stack

| Tool | Purpose |
|---|---|
| FastAPI | Web framework and routing |
| SQLAlchemy 2.0 | ORM and database abstraction |
| Alembic | Schema migration management |
| python-jose | JWT encoding and validation |
| bcrypt | Password hashing |
| Pydantic | Request/response validation |
| SQLite | Development database |

---

## Roadmap

- [ ] Transaction-safe booking overlap detection
- [ ] Booking approval workflow
- [ ] Administrative role management endpoints
- [ ] Automated testing with pytest
- [ ] Docker containerisation
- [ ] CI integration