Campus Booking System – Backend API

A backend service for a multi-user campus room booking platform built using FastAPI, SQLAlchemy 2.0, Alembic, and JWT-based authentication.

This project demonstrates structured backend architecture, stateless authentication, role-based access control (RBAC), and version-controlled database migrations.

Overview

The system simulates a campus room booking backend supporting multiple user roles with secure authentication and clear domain modeling.

Core capabilities include:

JWT authentication (OAuth2 password flow)

Role-based access control (STUDENT / STAFF / ADMIN)

SQLAlchemy 2.0 ORM models

Alembic migration management

Dependency-injected database sessions

Interactive Swagger documentation

Layered application architecture


Architecture

The application follows a layered structure:

app/
├── api/ Route handlers
├── core/ Configuration and security utilities
├── db/ Database engine and session management
├── models/ SQLAlchemy ORM models
├── schemas/ Pydantic request and response models

Design Principles

Explicit dependency injection

Stateless JWT authentication

Clean separation between transport layer and domain logic

Version-controlled schema migrations

Clear commit structure following conventional commits

Authentication & Authorization

Authentication uses OAuth2 password flow with JWT bearer tokens.

Flow:

User registers via POST /auth/register

User logs in via POST /auth/login

The API returns an access_token

The client includes the token in the request header:

Authorization: Bearer <access_token>

The token is validated and the user is loaded from the database using the get_current_user dependency.

Role-based authorization is enforced using reusable dependency guards such as:

require_roles("ADMIN")

Roles

STUDENT – Create and view bookings
STAFF – Manage rooms and approve bookings
ADMIN – Full system control

RBAC is enforced at the route level using dependency injection.

Database

SQLAlchemy 2.0 ORM

Alembic migrations

SQLite for development

PostgreSQL-ready configuration

Migrations ensure the schema remains version-controlled and reproducible.

Running Locally

Create a virtual environment

Activate it

Install dependencies from requirements.txt

Apply migrations using Alembic

Start the FastAPI server

API documentation is available at:

http://127.0.0.1:8000/docs

Example Endpoints

POST /auth/register
POST /auth/login
GET /auth/me

Roadmap

Transaction-safe booking overlap detection

Booking approval workflow

Administrative role management endpoints

Automated testing with pytest

Docker containerisation

CI integration

Tech Stack

FastAPI
SQLAlchemy 2.0
Alembic
python-jose (JWT)
bcrypt
Pydantic
SQLite

