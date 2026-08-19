# FlyRank Backend AI Engineering Internship

This repository documents my hands-on assignments, experiments, and technical work completed during the **FlyRank Backend AI Engineering Internship**.

The repository is organized by week so each assignment can be reviewed independently, while the full repository shows my progression from basic REST APIs to databases, containerized services, authentication, and secure backend engineering.

---

## Internship Focus

The Backend AI Engineering track focuses on practical backend foundations required for building reliable AI-powered applications.

Topics covered include:

* Python backend development
* FastAPI
* HTTP and REST APIs
* CRUD operations
* Input validation and error handling
* SQLite and PostgreSQL
* Database persistence
* Docker and containerization
* Environment variables and secret management
* Supabase Auth
* JWT authentication
* Protected API routes
* Authentication vs authorization
* Swagger UI / OpenAPI
* Git and GitHub workflows
* Production-oriented backend practices

---

## Repository Structure

```text
FlyRank-Backend-AI-Engineering/
│
├── README.md
│
├── Week-02/
│   └── CRUD-API/
│       ├── main.py
│       ├── requirements.txt
│       ├── README.md
│       └── screenshots/
│
├── Week-03/
│   └── CRUD-Database/
│       ├── main.py
│       ├── repository.py
│       ├── requirements.txt
│       ├── README.md
│       └── ...
│
└── Week-04/
    └── Auth-Login-Protect/
        ├── main.py
        ├── requirements.txt
        ├── .env.example
        ├── README.md
        └── screenshots/
```

Each substantial assignment contains its own documentation, setup instructions, implementation details, and testing evidence.

---

## Progress

| Week   | Assignment                                            | Key Concepts                                                                       | Status      |
| ------ | ----------------------------------------------------- | ---------------------------------------------------------------------------------- | ----------- |
| Week 2 | [Build Your First CRUD API](Week-02/CRUD-API/)        | FastAPI, HTTP, CRUD, validation, status codes, Swagger UI, Git                     | ✅ Completed |
| Week 3 | [Connecting to the Database](Week-03/CRUD-Database/)  | SQLite, SQL persistence, repository pattern, API/database integration              | ✅ Completed |
| Week 3 | [Containerize Your Stack](Week-03/CRUD-Database/)     | PostgreSQL, Docker, persistent volumes, psycopg, environment configuration         | ✅ Completed |
| Week 4 | [Auth · Login & Protect](Week-04/Auth-Login-Protect/) | Supabase Auth, JWT, protected routes, authorization, refresh tokens, rate limiting | ✅ Completed |

---

# Week 2 — Build Your First CRUD API

The first backend assignment was a REST API for managing an in-memory task list.

The API implements the complete CRUD cycle:

```text
Create → POST /tasks
Read   → GET /tasks and GET /tasks/{task_id}
Update → PUT /tasks/{task_id}
Delete → DELETE /tasks/{task_id}
```

### Key Work

* Built with Python and FastAPI
* Added root and health endpoints
* Implemented full task CRUD
* Added request validation
* Used correct HTTP status codes
* Added `404` handling for missing tasks
* Tested with curl and Swagger UI
* Developed incrementally with Git stage commits

➡️ [View Week 2 — CRUD API](Week-02/CRUD-API/)

---

# Week 3 — Connecting to the Database

The Week 2 API was upgraded from an in-memory task list to persistent database storage.

The API contract remained consistent while the underlying persistence layer changed.

### Key Work

* Replaced in-memory task storage with SQLite
* Created and initialized a `tasks` table
* Added database-backed CRUD operations
* Preserved existing API routes
* Added validation for empty update requests
* Verified successful create, read, update, and delete behavior
* Verified `404` responses for missing records

This assignment demonstrated that the API layer and persistence implementation can evolve independently when responsibilities are separated properly.

➡️ [View Week 3 — CRUD Database](Week-03/CRUD-Database/)

---

# Week 3 — Containerize Your Stack

The database-backed CRUD API was then upgraded from local SQLite storage to PostgreSQL running in Docker.

### Key Work

* Used PostgreSQL 17 in Docker
* Added persistent database storage
* Replaced the SQLite persistence implementation with PostgreSQL
* Used `psycopg` for database communication
* Preserved the existing FastAPI route behavior
* Moved database configuration into environment variables
* Added `.env.example`
* Kept the real `.env` outside Git
* Tested CRUD operations against PostgreSQL
* Verified database records directly

This assignment introduced a more realistic backend architecture:

```text
Client
  ↓
FastAPI
  ↓
Repository Layer
  ↓
PostgreSQL
  ↓
Docker Persistent Storage
```

➡️ [View Week 3 — Containerized Database API](Week-03/CRUD-Database/)

---

# Week 4 — Auth · Login & Protect

The Week 4 assignment introduced authentication and API security using **Supabase Auth**.

Instead of implementing password storage or cryptography manually, Supabase acts as the Identity Provider and issues signed JWT access tokens.

### Core Authentication Flow

```text
User
  ↓
Signup / Login
  ↓
Supabase Auth
  ↓
JWT Access Token
  ↓
Authorization: Bearer <token>
  ↓
FastAPI Authentication Dependency
  ↓
Supabase Token Verification
  ↓
Protected API Route
```

### Required Features Completed

* `POST /auth/signup`
* `POST /auth/login`
* `POST /auth/logout`
* `GET /public/info`
* `GET /protected/profile`
* Additional `GET /protected/dashboard`
* Supabase JWT verification
* Reusable FastAPI authentication dependency
* Swagger UI `HTTPBearer` authorization
* Proper `200`, `201`, `204`, `400`, and `401` responses
* Environment-based Supabase configuration
* Git-ignored `.env`
* Public `.env.example`
* Swagger authentication screenshot
* Stage-by-stage Git history

### Additional Security Features

The following optional stretch features were also implemented:

* Admin-only endpoint with a real `403 Forbidden` authorization case
* Refresh-token endpoint for obtaining fresh access tokens
* Failed-login rate limiting with `429 Too Many Requests`

Verified authorization behavior:

```text
Missing authentication      → 401 Unauthorized
Authenticated non-admin      → 403 Forbidden
Authenticated admin          → 200 OK
```

Verified login rate limiting:

```text
Failed login #1              → 401 Unauthorized
Failed login #2              → 401 Unauthorized
Failed login #3              → 401 Unauthorized
Additional attempt           → 429 Too Many Requests
Valid login after cooldown   → 200 OK
```

➡️ [View Week 4 — Auth · Login & Protect](Week-04/Auth-Login-Protect/)

---

## Git Workflow

Assignments are developed incrementally instead of being submitted as one large final commit.

Typical development stages include:

```text
Requirement
    ↓
Implementation
    ↓
Checkpoint test
    ↓
Git commit
    ↓
Next stage
```

For the authentication assignment, the required development history includes:

```text
Stage 0: setup server and supabase client
Stage 1: signup and login routes working
Stage 2: public route and unverified protected route
Stage 3: profile route token verification
Stage 4: auth middleware and logout endpoint
Stage 5: Swagger UI documentation with bearer auth
Stage 6: publish to GitHub and write README
```

Additional security improvements were committed separately.

---

## Security Practices

Across the backend assignments, the repository follows several important practices:

* Secrets are stored outside source code.
* Real `.env` files are ignored by Git.
* Example configuration is provided through `.env.example`.
* Password storage and hashing are delegated to a trusted Identity Provider.
* JWTs are verified before protected routes execute.
* Authentication logic is reusable rather than duplicated across routes.
* Authentication (`401`) and authorization (`403`) are treated separately.
* Login endpoints include basic brute-force protection.
* Database persistence is separated from API route logic where practical.

---

## Learning Approach

For each FlyRank assignment, I follow a stage-based workflow:

1. Read the official assignment requirements.
2. Understand the underlying backend concept.
3. Implement the solution incrementally.
4. Test both successful and failure cases.
5. Verify the implementation against the requirements.
6. Document setup and usage.
7. Preserve meaningful Git commits.
8. Publish submission-ready evidence to GitHub.

The objective is not only to complete each assignment, but to understand why the implementation works and how the same concepts apply to production backend systems.

---

## Author

**Abdullah Javed**

Robotics Engineering Student | AI/ML & Backend Engineering

* GitHub: [Abdullah-Javed-01](https://github.com/Abdullah-Javed-01)
* LinkedIn: [Abdullah Javed](https://www.linkedin.com/in/abdullah-javed-id01/)
