# Issues & Insights Tracker

## Project Description
A mini SaaS 'Issues & Insights Tracker' application for structured feedback analysis, built as a production-ready, Dockerized full-stack solution. Demonstrates idiomatic use of SvelteKit, FastAPI, and PostgreSQL, deployable with a single `docker compose up` command.

## Features
* **User Authentication:** Secure user registration and login.
* **Issue Management:** Create, view, update, and delete issues/feedback entries.
* **Real-time Updates:** (If applicable, mention any WebSocket/real-time features)
* **Robust Backend API:** RESTful API built with FastAPI.
* **Relational Database:** Data persistence using PostgreSQL.
* **Background Tasks:** (If using Celery for background tasks, mention here).
* **Containerized Environment:** Easily deployable via Docker and Docker Compose.

## Technologies Used

### Frontend
* **Framework:** SvelteKit (based on your project structure)
* **Styling:** Tailwind CSS (if applicable)
* **State Management:** Svelte Stores (if applicable)
* **Other:** HTML, CSS, JavaScript

### Backend
* **Framework:** FastAPI
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy (with Alembic for migrations)
* **Background Tasks:** Celery, Redis (for broker/backend)
* **Authentication:** JWT (JSON Web Tokens)
* **Web Server:** Uvicorn

### Infrastructure
* **Containerization:** Docker, Docker Compose
* **Reverse Proxy/Load Balancer:** Nginx (if configured)

## Architecture & Key Decisions

* **Monorepo Structure:** The project uses a monorepo approach with distinct `frontend/` and `app/` (backend) directories, managed within a single Git repository for streamlined development and deployment.
* **FastAPI Choice:** The backend is built with FastAPI for its high performance, automatic documentation, and excellent developer experience.
    * **[Refer to ADR 0001 for detailed decision on FastAPI](/docs/adr/0001-choose-fastapi.md)**
* **Containerization with Docker Compose:** The entire application is containerized to ensure consistent environments across development and production, facilitating easy setup and deployment.
* **Asynchronous Communication:** (If you used WebSockets or async tasks, mention how they enhance real-time capabilities or performance).
* **Database Migrations:** Alembic is used for robust database schema management, ensuring smooth updates.

## Setup and Installation

Follow these steps to get the application up and running on your local machine.

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
    ```bash
    docker compose up --build -d
    ```
    * The `-d` flag runs the containers in detached mode (in the background). Remove `-d` if you want to see logs directly in your terminal.

3.  **Perform database migrations (initial setup):**
    * Once containers are up, execute migrations within the `backend` service:
        ```bash
        docker compose exec backend alembic upgrade head
        ```
        * This creates the necessary tables in the PostgreSQL database.

4.  **Create initial superuser (optional, for admin access):**
    * You might need to create an initial user to access admin functionalities or seed data.
    * (Add instructions here if your app has a specific way to create an admin user, e.g., a FastAPI endpoint or a script. If not, just delete this step.)

## Running the Application

* **Backend API:**
    * Accessible at `http://localhost:8000/docs` (FastAPI interactive API documentation).
    * The main API endpoint will be `http://localhost:8000/api/v1/...` (adjust as per your API routes).
* **Frontend Application:**
    * Accessible at `http://localhost:5173/` (or whatever port your SvelteKit dev server runs on).
* **Celery Flower Dashboard:** (If you have Celery Flower for monitoring tasks)
    * Accessible at `http://localhost:5555/`

## Testing

To run the automated tests for the backend:

1.  Ensure your Docker containers are running (`docker compose up -d`).
2.  Execute tests within the backend service container:
    ```bash
    docker compose exec backend pytest
    ```
    * (Adjust `pytest` if you use a different test runner or specific test commands).

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

*(You will add your Loom video link here after recording it)*

[Link to Video Demo](YOUR_LOOM_VIDEO_LINK_HERE)

## AI Usage Disclosure

*(Add a brief statement here if you used any AI tools like Gemini, ChatGPT, GitHub Copilot for code generation, debugging, or documentation assistance. Example: "I utilized Google Gemini for assistance with clarifying Git commands and structuring documentation.")*

---