
## Implementation Workflow

This section outlines the step-by-step plan for building out the DRKR project, mapping directly to the file structure and technical specifications. Each subsection details the components to be built and integrated.

### 1. Project Config & Initialization
- **Environment Configuration:**  
  - Set up a `.env` file or configure environment variables in `backend/app/config.py` for items such as:
    - `DATABASE_URL` (PostgreSQL connection)
    - JWT secret keys and OAuth2 client IDs
    - Pinecone API key
  - Use `pydantic` to load these variables.
- **Database Connection:**  
  - In `backend/app/db/database.py`, create the SQLAlchemy engine and sessionmaker.
  - Configure Alembic for migrations and run the initial migration (e.g., `alembic upgrade head`).

### 2. Models & Schemas
- **Models:**  
  - Define SQLAlchemy models in `backend/app/models.py` for entities such as `User`, `DeepResearch`, and `ApiKey`.
  - Include necessary relationships and fields (e.g., user roles for RBAC).
- **Schemas:**  
  - Create corresponding Pydantic models in `backend/app/schemas.py` to validate and structure API inputs/outputs.
  - Ensure that `orm_mode = True` is set in schema configurations for compatibility with SQLAlchemy models.

### 3. Authentication & Authorization
- **OAuth2 & JWT Implementation:**  
  - Implement OAuth2 endpoints and JWT token generation in `backend/app/routers/auth.py`.
  - Develop helper functions in `backend/app/services/authentication.py` for token creation, validation, and RBAC enforcement.
- **API Keys:**  
  - Provide an endpoint or utility for generating API keys for external integrations and store them securely in the database.

### 4. Routers & Endpoints
- **User Endpoints (`routers/users.py`):**  
  - CRUD operations for user management, including endpoints like `/api/users/me` for fetching current user details.
- **Prompt Endpoints (`routers/prompts.py`):**  
  - Implement endpoints for creating, reading, updating, and deleting research prompts:
    - `GET /api/prompts` for listing prompts (with optional filters)
    - `POST /api/prompts` for creating new prompts
    - `GET /api/prompts/{id}`, `PUT/PATCH`, and `DELETE /api/prompts/{id}` for individual prompt operations.
- **Research Job Endpoints (`routers/research_jobs.py`):**  
  - Create endpoints to launch and monitor deep research tasks.
  - For instance, `POST /api/research-jobs` should queue a Celery task, and `GET /api/research-jobs/{id}` should return the status/results.

### 5. Services (Business Logic)
- **Research Service (`services/research.py`):**  
  - Orchestrate the deep research workflow: fetching prompt data, interfacing with LLMs, chunking texts, and storing results.
- **Pinecone Integration (`services/pinecone_service.py`):**  
  - Handle embedding generation and interactions with the Pinecone vector database.
- **Authentication Utilities (`services/authentication.py`):**  
  - Consolidate logic for JWT handling and OAuth2 integrations.

### 6. Celery Integration
- **Celery Configuration:**  
  - Set up Celery in `backend/app/core/celery_app.py` with Redis as the broker.
- **Defining Tasks:**  
  - In a dedicated file (or within `services/research.py`), define Celery tasks (e.g., a task to execute a deep research job).
  - Use `run_deep_research.delay(prompt_id)` in the relevant endpoint to trigger asynchronous processing.

### 7. Logging & Error Handling
- **Structured Logging:**  
  - Configure structured (JSON) logging in `backend/app/core/logging.py`.
  - Output logs to the `logs/backend.log` file for development, with plans to integrate ELK/Sentry in production.
- **Exception Handling:**  
  - Use FastAPI’s exception handlers to manage and return consistent error responses.
  - Implement custom error classes as needed.

### 8. Frontend Implementation (Using Vite & TypeScript)
- **Entry Point & Build Configuration:**  
  - The entry file is `src/main.tsx` which renders the main `<App />` component found in `src/App.tsx`.
  - Vite provides fast development and hot module replacement.
- **Routing & Component Structure:**  
  - Configure client-side routing using React Router in TypeScript.  
    - Define routes in `src/routes.tsx` or directly within `src/App.tsx`, ensuring type safety for route parameters.
    - Use the navigation component to navigate between routes.
- **API Service Integration:**  
  - Create an API service file in `src/services/api.ts` that uses Axios with proper TypeScript interfaces
    Create functions for:
      - login(credentials) -> calls /api/auth/token
      - fetchPrompts() -> calls GET /api/prompts
      - createPrompt(data) -> calls POST /api/prompts
      - startResearchJob(promptId) -> calls POST /api/research-jobs
    Handle token injection in headers.
- **Component Development:**  
  - Build components for:
    - **Authentication:** Login and user session management using OAuth or local (e.g., `src/components/Auth/Login.tsx`). 
    - **Prompts:** Listing, detail view, and creation forms (e.g., `src/components/Prompts/PromptsList.tsx`, `PromptDetail.tsx`)
    - **Research Jobs:** Display job status and results (e.g., `src/components/ResearchJobs/ResearchJobDetail.tsx`)
  - Use TypeScript interfaces to define props and state for each component, ensuring compile-time type safety.
- **Styling & Assets:**  
  - Manage styles via Tailwind CSS, ensuring that styles are maintained within the TypeScript/React ecosystem.
- **Development & Testing:**  
  - Start the development server with:
    ```bash
    npm run dev
    ```
  - Write tests using tools like Jest and React Testing Library with TypeScript support.

### 9. Testing & Validation
- **Backend Testing:**  
  - Write unit and integration tests in `backend/tests/` for endpoints, Celery tasks, and service functions.
- **Frontend Testing:**  
  - Create tests using Jest and React Testing Library to validate component functionality and API integrations.
- **End-to-End Testing:**  
  - Optionally use Cypress or Playwright to simulate user interactions across the entire stack.

### 10. Deployment Planning
- **Local Docker Compose (Optional):**  
  - Create a `docker-compose.yml` to spin up containers for FastAPI, PostgreSQL, Redis, and optionally the Vite-built frontend.
- **Production Deployment:**  
  - Containerize the backend and frontend for production.
  - Ensure proper handling of environment variables and secure configurations.
  - Set up a deployment pipeline to run migrations, start Celery workers, and serve the React app (static build served via a CDN or Nginx).
