# FlyRank Backend AI Engineering Internship

This repository documents my hands-on work, assignments, experiments, and technical learning completed during the **FlyRank AI Backend AI Engineering Internship**.

The repository is organized by week so each assignment can be reviewed independently while the full repository shows my overall progression through backend and applied AI engineering concepts.

---

## Internship Focus

The Backend AI Engineering track focuses on building practical foundations for developing AI-powered backend systems.

Topics covered through the internship include:

- Backend development fundamentals
- HTTP and the request-response cycle
- REST APIs
- CRUD operations
- API validation and error handling
- FastAPI
- Git and GitHub workflows
- API documentation
- LLM and AI application development
- Retrieval and grounded AI systems
- Evaluation and production-oriented AI workflows

---

## Repository Structure

```text
FlyRank-Backend-AI-Engineering/
│
├── README.md
├── .gitignore
│
├── Week-02/
│   └── CRUD-API/
│       ├── main.py
│       ├── requirements.txt
│       ├── README.md
│       └── screenshots/
│
├── Week-03/
│   └── ...
│
└── ...
```

Each substantial assignment contains its own README with setup instructions, implementation details, testing evidence, and learning outcomes.

---

## Progress

| Week | Assignment / Project | Key Concepts | Status |
|---|---|---|---|
| Week 2 | [Build Your First CRUD API](Week-02/CRUD-API/) | HTTP, CRUD, FastAPI, validation, status codes, Swagger UI, Git | ✅ Completed |
| Week 3 | Upcoming | — | ⏳ Not Started |

This table will be updated as the internship progresses.

---

# Week 2 — Build Your First CRUD API

The first backend project is a REST API for managing an in-memory to-do list.

The API implements the four core CRUD operations:

```text
Create → POST /tasks
Read   → GET /tasks and GET /tasks/{task_id}
Update → PUT /tasks/{task_id}
Delete → DELETE /tasks/{task_id}
```

### Technologies

- Python 3.12
- FastAPI
- Uvicorn
- Swagger UI / OpenAPI
- Git
- GitHub

### Implemented Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check |
| `GET` | `/tasks` | List all tasks |
| `GET` | `/tasks/{task_id}` | Get one task |
| `POST` | `/tasks` | Create a task |
| `PUT` | `/tasks/{task_id}` | Update a task |
| `DELETE` | `/tasks/{task_id}` | Delete a task |

### HTTP Status Codes Practiced

- `200 OK`
- `201 Created`
- `204 No Content`
- `400 Bad Request`
- `404 Not Found`

The complete CRUD cycle was tested using both **curl** and **Swagger UI**.

➡️ [View the complete Week 2 CRUD API project](Week-02/CRUD-API/)

---

## Git Workflow

The CRUD API was developed incrementally rather than as one large final commit.

The implementation followed stage-based commits including:

```text
Stage 0: hello server
Stage 1: root and health endpoints
Stage 2: read endpoints with 404
Stage 3: create with validation
Stage 4: full CRUD
Stage 5: Swagger UI
```

Additional improvements were committed separately after reviewing the API documentation and testing evidence.

This approach preserves the development process and makes individual implementation stages easier to review.

---

## Learning Approach

The goal of this repository is not only to complete internship assignments, but to understand the engineering concepts behind them.

For each project I focus on:

1. Understanding the requirement
2. Learning the underlying concept
3. Implementing the solution incrementally
4. Testing expected and failure cases
5. Reviewing the implementation
6. Documenting the result
7. Committing meaningful development stages

---

## Author

**Abdullah Javed**

Robotics Engineering Student | AI/ML & Data Analytics

- GitHub: [Abdullah-Javed-01](https://github.com/Abdullah-Javed-01)
- LinkedIn: [Abdullah Javed](https://www.linkedin.com/in/abdullah-javed-id01/)
