# technical_overview.md
--

# Backend
## Authentication & Authorization:
	OAuth2 with OpenID Connect (Auth0) to offload password handling. After authentication, issue JWT tokens for stateless session management (allowing the API to validate user identity without server-side sessions). For API clients or integrations, provide API keys for access – generate random tokens and associate them with user accounts. Ensure tokens are transmitted over TLS and stored securely (use HttpOnly cookies or secure storage to mitigate XSS/CSRF). Role-based access control (RBAC) should be enforced in the API (define user roles or scopes to restrict certain endpoints).

## API Framework:
	FastAPI in Python

## Structured Database:
	PostgreSQL

## Background Processing:
	Celery + Redis

## Search & Indexing:
	PostgreSQL full-text search
	pgvector for vector similarity

## Logging:
	Structured logging should be used on the backend (JSON) so logs can be easily parsed; include context like request IDs or user IDs for traceability.
	For MVP stage: File-based log streaming
	Finished product: ELK for logs and Sentry for error tracking

## Vector Database:
	Pinecone

## Testing:
	PyTest
--

# Frontend
## UI Framework:
	Vite + TypeScript + React + Tailwind CSS + React Router + React Query

## REST API Design:
	Design a clean RESTful API that the frontend (and other clients) will use to interact with the backend. Follow best practices for resource-oriented endpoints and HTTP methods. Use noun-based URLs for resources (e.g. /api/prompts for listing or creating research prompts, /api/prompts/{id} for retrieving a specific prompt’s details) – avoid verbs in endpoint names since the HTTP method implies the action (GET for read, POST for create, etc.). Each major data entity (Prompt, ResearchOutput, User, etc.) should have its own endpoint. Support filtering and querying via query parameters (for example, GET /api/prompts?userId=123&tag=history). Implement proper HTTP methods: GET for reads, POST for creating new records (e.g., submitting a new research prompt), PUT/PATCH for updates (e.g., editing a prompt’s metadata or adding notes), DELETE for removal. The API should return standard HTTP status codes (200/201 for success, 400 for bad requests, 401/403 for auth errors, 500 for server errors, etc.) to make it easy to handle responses. Embrace statelessness – each request from the React app includes authentication (e.g. the JWT in an Authorization header or cookie) so that servers can be scaled without sticky sessions. The data format should be JSON (or JSON:API spec if you prefer a standard convention), with clear structure. For example, a GET response for prompts might look like an array of prompt objects with fields like id, title, content, createdAt, createdBy. When the user triggers a “deep research” action, the frontend might POST to /api/research-jobs with the prompt details, and the backend responds with a job ID and status. The frontend can then poll or use websockets (if implemented) to get the output when ready. Document the API – using an OpenAPI (Swagger) definition is very helpful for both development and future third-party integration. You can generate this automatically with frameworks (FastAPI generates a Swagger UI, DRF can generate an OpenAPI schema, etc.). Also, consider versioning the API (e.g., prefix routes with /v1/) so that future changes can be made without breaking old clients. Keep the API consistent and predictable: for instance, use plural nouns for collections, and nest sub-resources if needed (e.g., /api/users/{id}/prompts for prompts by a specific user). This consistency improves developer experience and reduces errors. Lastly, implement CORS properly so that the React frontend (likely served from a different origin during development, e.g. localhost:3000) can make requests to the API domain.

## Data Handling & UX:
	On the frontend, make sure to handle API calls gracefully. Use loading indicators when fetching data or submitting forms, and handle errors returned by the API (display user-friendly messages, especially for validation errors or auth issues). Implement client-side routing for a smooth single-page app experience Use React Router to manage URL -> component mapping, e.g., /prompts/123 route to a PromptDetail component. Use local storage or context to cache some data client-side (for instance, store the last viewed prompts or user token).

## API Integration & Testing:
	- Ensure the API endpoints are designed in a RESTful way that is easy to consume from the React app. For example, after the user submits a new prompt via a form, the React app calls POST /api/prompts and upon success, perhaps navigates to the detail page for that prompt (using the ID returned). Use token-based authentication for API calls (e.g., include Authorization: Bearer <JWT> header in fetch calls). It’s wise to create a small API wrapper or use a React Query library to manage the API calls and caching. Also implement CSRF protection if using cookies for auth.
	- For testing, write integration tests using Jest + React Testing Library for frontend, and PyTest or Mocha for backend to ensure the end-to-end flow works.

--

Maintain a clear separation: the React frontend is purely for presentation and user interaction, and all data/state is fetched or mutated via the REST API. This separation will also allow future possibilities like third-party clients or a mobile app to use the same API.
