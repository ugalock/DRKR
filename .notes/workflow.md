# Implementation Workflow

This section outlines the step-by-step plan for building out the DRKR project, mapping directly to the file structure and technical specifications. Each subsection details the components to be built and integrated.

## 1. Project Config & Initialization
[✔] **Environment Configuration:**  
  [✔] Set up a `.env` file or configure environment variables in `backend/app/config.py` for items such as:
    [✔] `DATABASE_URL` (PostgreSQL connection)
    [✔] JWT secret keys and OAuth2 client IDs
    [✔] Pinecone API key
  [✔] Use `pydantic` to load these variables.
[✔] **Database Connection:**  
  [✔] In `backend/app/db/database.py`, create the SQLAlchemy engine and sessionmaker.
  [✔] Configure Alembic for migrations and run the initial migration (e.g., `alembic upgrade head`).

## 2. Models & Schemas
[✔] **Models:**  
  [✔] Define SQLAlchemy models in `backend/app/models.py` for entities such as `User`, `DeepResearch`, and `ApiKey`.
  [✔] Include necessary relationships and fields (e.g., user roles for RBAC).
[✔] **Schemas:**  
  [✔] Create corresponding Pydantic models in `backend/app/schemas.py` to validate and structure API inputs/outputs.
  [✔] Ensure that `orm_mode = True` is set in schema configurations for compatibility with SQLAlchemy models.

## 3. Authentication & Authorization
[✔] **OAuth2 & JWT Implementation:**  
  [✔] Implement OAuth2 endpoints and JWT token generation in `backend/app/routers/auth.py` for Auth0.
  [✔] Develop helper functions in `backend/app/services/authentication.py` for token creation, validation, and RBAC enforcement.
[✔] **API Keys:**  
  [✔] Provide an endpoint or utility for generating API keys for external integrations and store them securely in the database.

## 4. Routers & Endpoints
[✔] **User Endpoints (`routers/users.py`):**  
  [✔] CRUD operations for user management, including endpoints like `/api/users/me` for fetching current user details.
[✔] **Research Job Endpoints (`routers/research_jobs.py`):**  
  [✔] Create endpoints to launch and monitor deep research tasks.
  [✔] For instance, `POST /api/research-jobs` should queue a Celery task, and `GET /api/research-jobs/{id}` should return the status/results.
[✔] **Deep Research Endpoints (`routers/deep_research.py`):**
  [✔] ...

## 5. Services (Business Logic)
[✔] **Research Service (`services/research.py`):**  
  [✔] Orchestrate the deep research workflow: fetching prompt data, interfacing with LLMs, chunking texts, and storing results.
[✔] **Pinecone Integration (`services/pinecone_service.py`):**  
  [✔] Handle embedding generation and interactions with the Pinecone vector database.
[✔] **Authentication Utilities (`services/authentication.py`):**  
  [✔] Consolidate logic for JWT handling and OAuth2 integrations.

## 6. Celery Integration
[✔] **Celery Configuration:**  
  [✔] Set up Celery in `backend/app/core/celery_app.py` with Redis as the broker.
[✔] **Defining Tasks:**  
  [✔] In a dedicated file (or within `services/research.py`), define Celery tasks (e.g., a task to execute a deep research job).
  [✔] Use `run_deep_research.delay(prompt_id)` in the relevant endpoint to trigger asynchronous processing.

## 7. Logging & Error Handling
[ ] **Structured Logging:**  
  [ ] Configure structured (JSON) logging in `backend/app/core/logging.py`.
  [ ] Output logs to the `logs/backend.log` file for development, with plans to integrate ELK/Sentry in production.
[ ] **Exception Handling:**  
  [ ] Use FastAPI's exception handlers to manage and return consistent error responses.
  [ ] Implement custom error classes as needed.

## 8. Frontend Implementation (Using Vite & TypeScript)
### 8.1. Environment & Basic Setup
1. **Initialize Dependencies**  
   [✔] Install React, TypeScript, Tailwind, React Router, React Query.  
   [✔] Confirm your `package.json` is up to date.  
   [✔] **AI Reminder**: Keep watch for missing or deprecated libraries and propose alternatives if needed.

2. **Confirm Directory Structure**  
   [✔] Run the shell script (or manually create) the updated `src/` folders and files.

### 8.2. Global Config & App Shell
1. **`main.tsx` Setup**  
   [✔] Import global providers: `<BrowserRouter>`, `<QueryClientProvider>`, etc.  
   [✔] Render `<App />` into `root`.  
   [✔] **AI Reminder**: If environment variables differ between dev and prod, note them for build steps.

2. **`App.tsx` & `index.css`**  
   [✔] Create a top-level layout (nav, sidebar if any, footer).  
   [✔] Include Tailwind's directives in `index.css`.  
   [✔] **AI Reminder**: Make sure the layout aligns with RBAC contexts (public vs. org pages).

### 8.3. Routing & Authentication
1. **`routes/index.tsx`**  
   [✔] Set up `Routes` and `Route` paths for home, login, research items, etc.  
   [✔] Handle public routes vs. private org routes with a guard or context-based condition.  
   [✔] **AI Reminder**: The AI can detect missing routes or incomplete coverage (like forgot password or 404) and suggest corrections.

2. **`services/authService.ts`** & **`context/AuthContext.tsx`**  
   [✔] Implement logic for JWT storage, login, logout, token refresh.  
   [✔] Provide an `AuthContext` to share user state (roles, permissions).  
   [✔] **AI Reminder**: Watch for edge cases in token expiration or logout flows.

### 8.4. API Layer & React Query Configuration
1. **Axios & Query Client**  
   [✔] In `hooks/useApi.ts`, configure base URL, interceptors for JWT.  
   [✔] In `services/queryClient.ts`, create the `QueryClient` with caching/retry rules.  
   [✔] **AI Reminder**: Suggest best practices (e.g., exponential backoff, offline support) if relevant.

2. **Endpoints**  
   [✔] `userApi`, `researchApi`, `tagsApi`, etc. implemented in `hooks/useApi.ts`
   [✔] Implement each function to **CRUD** data from the backend.  
   [✔] **AI Reminder**: Confirm endpoints align with the backend's routes (FastAPI). Flag mismatches in request/response formats. ALWAYS CHECK THE BACKEND FOR SCHEMA DEFINITIONS.

### 8.5. Page-Level Components
1. **`pages/Home/`**  
   [✔] Show a dashboard or feed of recent "deep research" items (public and  user/org-specific).
   [✔] Optionally highlight top tags or trending items.  
   [✔] **AI Reminder**: Provide quick navigation for new user sign-up or login flows.

2. **`pages/Auth/`**  
   [✔] Login and register pages. Possibly an OAuth callback route.  
   [✔] **AI Reminder**: Ensure form validation and helpful error messages.

3. **`pages/Research/`**  
   [ ] List all accessible deep research items.  
   [ ] Detail page with the prompt, final report, multi-length summaries, comments, ratings.  
   [ ] **AI Reminder**: Mind user roles for editing or deleting items. Suggest guard checks.

4. **`pages/Tags/`**  
   [ ] Display sub-reddit–style channels by pre-approved tags.  
   [ ] Let moderators validate or approve posts.  
   [ ] **AI Reminder**: Suggest a filtering system for tags (global, org, user).

5. **`pages/Organization/`**  
   [ ] Pages for org membership management, inviting users, assigning roles.  
   [ ] **AI Reminder**: Manage "private," "org," or "public" scoping effectively in the UI.

### 8.6. Feature Modules & Custom Hooks
1. **`features/deepResearch/`**  
   [ ] Reusable logic for chunk retrieval, rating, multi-length summaries.  
   [ ] **AI Reminder**: Merge data from `researchApi.ts` with React Query patterns.

2. **`features/tags/` & `features/organizations/`**  
   [ ] Manage creation/editing of tags, org membership, etc.  
   [ ] **AI Reminder**: If repeated code is found across features, propose common hooks.

3. **`hooks/useAuth.ts`**, **`hooks/useFetchOrg.ts`**  
   [ ] Shared business logic for authentication checks, fetching org details, etc.  
   [ ] **AI Reminder**: Surface performance issues or potential infinite loops with custom hooks.

### 8.7. Store / Context
1. **Global State**  
   [ ] If using Redux or Zustand in `store/`, set up slices for user info, org data, etc.  
   [ ] Alternatively, rely on React Context.  
   [ ] **AI Reminder**: Watch for collisions between local component states, context, and query caching.

2. **Organization & Auth Context**  
   [ ] `OrgContext.tsx` to store current org ID, roles.  
   [ ] `AuthContext.tsx` for user token, role checks, etc.  
   [ ] **AI Reminder**: Confirm contexts don't overlap or cause re-renders across the app.

### 8.8. Shared Components & Utilities
1. **`components/common/`**  
   [ ] Build small, reusable UI parts (modals, buttons, spinners, etc.).  
   [ ] **AI Reminder**: Keep them themeable (dark mode or custom colors), if required.

2. **`utils/`** (`constants.ts`, `formatters.ts`)  
   [ ] Move repeated logic (e.g., date/time format, parse enum states) into these helpers.  
   [ ] **AI Reminder**: Centralize magic strings like `'public'`, `'org'`, `'private'` in `constants.ts` to avoid typos.

3. **`types/`**  
   [ ] Align front-end interfaces with the backend's Pydantic models.
   [ ] `research.d.ts` for the deep research schema, `user.d.ts` for user data, etc.  
   [ ] **AI Reminder**: If the backend changes the schema, flag outdated type definitions.

### 8.9. Testing & Quality Assurance
1. **Component Tests**  
   [ ] Use frameworks like Jest + React Testing Library.  
   [ ] Check rendering of pages, hook correctness (especially around RAG-based searches).  
   [ ] **AI Reminder**: Detect coverage gaps if major routes or state transitions are untested.

2. **Integration Tests**  
   [ ] Mock API calls to verify that pages work end-to-end (e.g., create research item, see it in UI).  
   [ ] **AI Reminder**: Ensure environment variables for test vs. dev are consistent.

3. **Linting & Formatting**  
   [ ] Implement ESLint + Prettier for code consistency.  
   [ ] **AI Reminder**: Enforce a style guide to keep code uniform.

### 8.10. Deployment & Iteration
1. **Build & Deploy**  
   [ ] Confirm environment variables (`API_URL`, etc.) for production.  
   [ ] Generate a production build via Vite.  
   [ ] **AI Reminder**: Validate final build is served from correct base path.

2. **Ongoing Iterations**  
   [ ] Add advanced features: domain co-occurrence graphs, RAG improvements, crowd-sourced rating expansions.  
   [ ] **AI Reminder**: Identify repeated code patterns or performance bottlenecks as the app grows.

## 9. Testing & Validation
[ ] **Backend Testing:**  
  [ ] Write unit and integration tests using PyTest in `backend/tests/` for endpoints, Celery tasks, and service functions.
[ ] **Frontend Testing:**  
  [ ] Create tests using Jest and React Testing Library to validate component functionality and API integrations.
[ ] **End-to-End Testing:**  
  [ ] Optionally use Cypress or Playwright to simulate user interactions across the entire stack.

## 10. Deployment Planning
[ ] **Local Docker Compose (Optional):**  
  [ ] Create a `docker-compose.yml` to spin up containers for FastAPI, PostgreSQL, Redis, and optionally the Vite-built frontend.
[ ] **Production Deployment:**  
  [ ] Containerize the backend and frontend for production.
  [ ] Ensure proper handling of environment variables and secure configurations.
  [ ] Set up a deployment pipeline to run migrations, start Celery workers, and serve the React app (static build served via a CDN or Nginx).
