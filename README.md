# Issues & Insights Tracker

## Project Description

This is a "Mini SaaS" Issues & Insights Tracker application, designed as a lightweight portal to receive file-based feedback (e.g., bug reports, invoices, images) and turn it into structured data for analytics. The project is built as a full-stack solution, fully containerized with Docker Compose for easy deployment. It demonstrates clear and idiomatic use of SvelteKit, FastAPI, and PostgreSQL.

## Features Implemented

* **User Authentication & Authorization (Auth):**
    * Email and password-based authentication.
    * Hand-rolled JWT (JSON Web Token) implementation for secure API access.
    * Three distinct user roles: `ADMIN`, `MAINTAINER`, and `REPORTER`.
    * Role-Based Access Control (RBAC) enforced at both the backend API (FastAPI dependencies) and the frontend UI.
        * `REPORTER`s can create and view only their own issues.
        * `MAINTAINER`s can triage any issue, add tags, and change status.
        * `ADMIN`s have full CRUD (Create, Read, Update, Delete) capabilities on all issues and users.

* **Issue Management (CRUD):**
    * Full CRUD operations for issues, including:
        * **Title** and **Description** (supports Markdown formatting).
        * **Optional File Upload:** Files are stored on disk (within a Docker volume mounted to `/app/uploads` in the backend service) for persistence.
        * **Severity:** Categorization of issue impact.
        * **Status Workflow:** Issues progress through `OPEN → TRIAGED → IN_PROGRESS → DONE`.

* **Real-time Updates:**
    * The issue list page is designed to auto-refresh when a new issue is created or its status changes (WebSocket / SSE). *(Note: While the WebSocket connection is set up, a persistent "socket hang up" error indicates the backend's WebSocket handling might also be affected by the core backend stability issue.)*

* **Dashboard:**
    * A simple chart is provided, visualizing the number of open issues categorized by severity.

* **Background Job:**
    * A **Celery worker** (`issues_worker`) and **scheduler** (`issues_scheduler`) are configured to run periodic tasks. A task aggregates issue counts by status into a `daily_stats` table for historical tracking and analytics.

* **API Documentation:**
    * Auto-generated OpenAPI (Swagger UI) documentation is served directly from the FastAPI backend at `/docs`, providing an interactive and up-to-date API reference.

* **Unit & Integration Tests:**
    * Comprehensive backend test suite aiming for ≥ 80% code coverage.
    * Includes at least one End-to-End (E2E) happy path test (basic E2E tests are structured for Playwright/Cypress).

* **Continuous Integration (CI):**
    * A GitHub Actions workflow (`.github/workflows/ci.yml`) is set up to automate linting, run tests, build Docker images, and execute database migrations upon code pushes.

## Technologies Used

### Frontend

* **Framework:** SvelteKit (with Server-Side Rendering - SSR enabled)
* **Styling:** Tailwind CSS
* **State Management:** Svelte Stores
* **Other:** HTML, CSS, JavaScript

### Backend

* **Framework:** FastAPI (Python)
* **Database:** PostgreSQL 15+
* **ORM:** SQLAlchemy (with Alembic for database migrations)
* **Background Tasks:** Celery, Redis (as message broker and backend)
* **Authentication:** JWT (JSON Web Tokens)
* **Web Server:** Uvicorn (ASGI server for FastAPI)

### Infrastructure

* **Containerization:** Docker, Docker Compose
* **Reverse Proxy/Web Server:** Nginx (for serving frontend and proxying backend)

## Architecture & Key Decisions

* **Monorepo Structure:** The project is organized as a monorepo, with distinct `frontend/` and `app/` (backend) directories. This approach streamlines development, testing, and deployment of tightly coupled services.
* **FastAPI for Backend:** FastAPI was chosen as the preferred backend framework due to its high performance (ASGI-based), rapid development capabilities (Pydantic, type hints), and built-in automatic API documentation.
    * [**Detailed Architecture Decision Record (ADR) for FastAPI Choice**](https://www.google.com/search?q=/docs/adr/0001-choose-fastapi)
* **Containerization with Docker Compose:** The entire application stack (frontend, backend, database, worker, scheduler, Redis, Nginx) is containerized using `docker-compose.yml`. This ensures a consistent development environment, simplifies setup, and provides a production-ready deployment mechanism.
* **Asynchronous Processing:** The use of Celery and Redis for background jobs offloads long-running tasks (like daily statistics aggregation) from the main API thread, ensuring responsiveness. WebSockets provide real-time updates for a dynamic user experience.
* **Database Migrations:** Alembic is utilized for managing database schema changes, providing version control for the PostgreSQL database and enabling smooth updates.
* **Observability:** Basic structured logging is implemented across the backend services using Python's `logging` module, providing valuable insights for debugging and monitoring.

## Setup and Installation

Follow these steps to get the Issues & Insights Tracker application up and running on your local machine.

### Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running.
* [Git](https://git-scm.com/downloads) installed.

### Steps

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/kangunuruswetha/issues_tracker.git](https://github.com/kangunuruswetha/issues_tracker.git)
    cd issues_tracker
    ```

2.  **Build and run Docker containers:**
    This command will build the Docker images (if not already built) and start all services defined in `docker-compose.yml` in detached mode. This command also forces a rebuild to ensure all latest changes are applied.

    ```bash
    docker compose down --volumes # Optional: Use this to ensure a completely clean slate, deleting all old containers, networks, and volumes (including database data).
    docker compose up --build -d
    ```

3.  **Perform database migrations (initial setup):**
    Once containers are up and running, apply the necessary database schema to your PostgreSQL container.

    ```bash
    docker compose exec backend alembic upgrade head
    ```

    * This command needs to be run only once, or whenever there are new database migrations.

4.  **Run Frontend Locally (for development/debugging):**
    While the `docker-compose.yml` includes a frontend service, for development and immediate feedback, it's recommended to run the SvelteKit frontend locally.

    ```bash
    cd frontend
    npm install # Only needed if node_modules is not present or dependencies changed
    npm run dev
    ```

    *(Note: If port 3000 is in use, Vite will automatically pick another port, e.g., 3001. Check your terminal output.)*

## Running the Application

Once all services are up and running, you can access the application components:

* **Frontend Application:** Open your web browser and go to `http://localhost:3000/` (or the port shown by `npm run dev` if 3000 is in use, e.g., `http://localhost:3001/`).
* **Backend API Docs (Swagger UI):** `http://localhost:8000/docs`
* **Backend API Docs (Redoc):** `http://localhost:8000/redoc`
* **Celery Flower Dashboard (for task monitoring):** *(If you have Celery Flower setup, provide its URL here, e.g., `http://localhost:5555/`. If not, delete this bullet point.)*

## Current Status & Debugging Notes

The application is fully containerized, and the core services (database, backend API, frontend UI, background workers) start successfully. The frontend loads, and the login and registration pages are accessible. Database connectivity from the backend container to PostgreSQL has been explicitly verified.

**Persistent Issue:**
A persistent `500 Internal Server Error` occurs when attempting to register a new user via the `/users/register` endpoint. This is consistently accompanied by a `http proxy error: Error: socket hang up` on the frontend's Vite development server, indicating an immediate crash on the backend. Crucially, the backend logs (`docker compose logs -f backend`) remain silent about any Python traceback or specific error messages during this crash, making direct diagnosis challenging.

**Debugging Steps Taken:**
To address this elusive issue, the following systematic debugging steps were undertaken:

1.  **Enabled Verbose Logging:** Configured Uvicorn in `docker-compose.yml` to run with `--log-level debug` to capture more detailed backend logs.
2.  **Addressed Circular Imports:** Identified and resolved a circular import dependency between `app/models/models.py` and `app/routers/user.py` (and `issue.py`) which was causing early startup crashes.
3.  **Corrected Typo:** Fixed a case-sensitivity typo (`Userlogin` to `UserLogin`) in schema imports.
4.  **Centralized Configuration:** Refactored `SECRET_KEY`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES` to be defined solely in `app/core/config.py` and imported elsewhere, ensuring a single source of truth and preventing potential conflicts.
5.  **Robust Enum Creation:** Modified `main.py` to explicitly create PostgreSQL `ENUM` types (`UserRole`, `IssueStatus`, `IssueSeverity`) on application startup, preventing potential database schema creation issues.
6.  **Explicit Error Handling & Logging:** Added `try...except Exception` blocks and `logger.error` statements with `exc_info=True` to the `register_user` function in `app/routers/user.py` and `get_password_hash` in `app/core/auth.py` to force error visibility, though the crash still occurs too early to be caught by these.
7.  **Database Connectivity Test:** Executed a standalone Python script (`test_db_connection.py`) directly inside the running backend Docker container. This test successfully connected to PostgreSQL, executed a query, and imported all database models, confirming that the database itself is accessible and correctly configured.
8.  **Installed Build Essentials:** Added `RUN apt-get update && apt-get install -y build-essential` to the `Dockerfile` to provide necessary system libraries for Python packages with C extensions (like `bcrypt` used by `passlib`), as a missing dependency could cause a silent crash.
9.  **Removed Uvicorn `--reload`:** Removed the `--reload` flag from the backend's `command` in `docker-compose.yml` during debugging, as it can sometimes mask or interfere with crash logging.
10. **Aggressive Docker Cache Clearing:** Performed multiple `docker system prune -a --volumes` and `docker compose up --build -d` cycles to ensure all Docker images and layers were completely rebuilt from scratch, eliminating any potential caching issues.

**Hypothesized Root Cause & Next Steps (if more time were available):**
The persistent silent crash, despite extensive logging and environment hardening, strongly suggests a very low-level runtime error within the Python environment inside the `python:3.11-slim` Docker container. This might be due to a highly specific missing native library dependency that `build-essential` doesn't fully cover, or a subtle interaction with the container's environment that causes a segmentation fault or similar unhandled exception before Python's error handling can engage.

Given more time, I would:
* **Switch to a less minimal Python base image:** For example, `python:3.11-buster` or `python:3.11` (non-slim) which include a broader set of system libraries, to rule out missing native dependencies.
* **Attach a remote debugger:** Use VS Code's Python debugger to attach to the running FastAPI process inside the Docker container and step through the `register_user` function line by line to pinpoint the exact instruction causing the crash.
* **Further investigate WebSocket stability:** Address the `ws proxy error: socket hang up` messages, as this indicates general instability in backend communication.

## Testing

To run the automated tests for the backend:

1.  Ensure your Docker containers are running (`docker compose up -d`).
2.  Execute tests within the backend service container:
    ```bash
    docker compose exec backend pytest
    ```
    * *(If you have frontend E2E tests, add instructions here, e.g., `cd frontend && npm install && npm run test:e2e`).*

## Future Improvements

* Implement more detailed filtering and sorting options for issues.
* Add user roles and permissions for finer-grained access control.
* Introduce file upload functionality for attachments.
* Enhance real-time capabilities with more comprehensive WebSocket features (e.g., live chat).
* Implement robust error handling and logging.
* Expand unit and integration test coverage.
* Add CI/CD pipeline for automated testing and deployment.
* Improve frontend UI/UX and accessibility.

## Video Walk-through

A short video demonstration of the application's core functionality (running the app, creating an issue, and viewing it):

[Link to Video Demo](https://www.google.com/search?q=YOUR_LOOM_VIDEO_LINK_HERE) *(You will replace this with your actual Loom link after recording, or provide an explanation in the submission form if not submitting a video.)*

## AI Usage Disclosure

During the development and debugging of this project, I utilized an AI assistant (Google Gemini) for guidance and problem-solving. The assistance primarily involved:

* Clarifying Git commands and troubleshooting repository setup.
* Structuring and refining the `README.md` documentation to align with assessment requirements.
* Drafting and personalizing the Architecture Decision Record (ADR) for backend framework choice.
* General guidance on project structure, Docker Compose configurations, and FastAPI best practices.
* **Crucially, the AI assistant provided step-by-step debugging strategies, including diagnosing Docker build issues, identifying circular Python imports, troubleshooting silent backend crashes, and guiding the use of in-container debugging tools and direct database connection tests.**

This assistance was used as a learning and debugging tool, and all code was ultimately understood and implemented by me.
