# DRKR Project File Structure

.
├── README.md
├── LICENSE
├── .gitignore
├── docker-compose.yml          # Or a minimal Docker setup for local development (optional)
├── backend
│   ├── app
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI entry point
│   │   ├── config.py           # Configuration settings (DB URL, Pinecone API Key, etc.)
│   │   ├── models.py           # SQLAlchemy models for Postgres (Prompt, User, ResearchOutput, etc.)
│   │   ├── schemas.py          # Pydantic models (request/response)
│   │   ├── routers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # OAuth2 endpoints & JWT logic
│   │   │   ├── prompts.py      # CRUD endpoints for prompts
│   │   │   ├── users.py        # CRUD endpoints for users
│   │   │   └── research_jobs.py# Endpoints for launching "deep research"
│   │   ├── services
│   │   │   ├── authentication.py  # Helper functions for JWT, role checks, etc.
│   │   │   ├── pinecone_service.py # Interactions with Pinecone
│   │   │   └── research.py     # Logic for orchestrating a research job
│   │   ├── core
│   │   │   ├── celery_app.py   # Celery configuration and init
│   │   │   └── logging.py      # Structured logging setup (JSON logs)
│   │   └── db
│   │       ├── database.py     # SQLAlchemy session & engine
│   │       └── migrations      # Alembic migrations folder
│   ├── tests
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_prompts.py
│   │   └── test_research_jobs.py
│   └── requirements.txt        # Python dependencies
├── frontend
│   ├── public                  # Static files (favicons, etc.)
│   ├── src
│   │   ├── index.js            # React entry point
│   │   ├── App.js              # Main App component / routing layout
│   │   ├── services
│   │   │   └── api.js          # API wrapper (fetch, axios, React Query, etc.)
│   │   ├── components
│   │   │   ├── Auth            # Auth-related components (Login, etc.)
│   │   │   ├── Prompts         # Prompt listing, creation, detail
│   │   │   └── ResearchJobs    # Possibly for viewing job progress/results
│   │   ├── pages
│   │   │   ├── Home.js
│   │   │   ├── PromptsPage.js
│   │   │   ├── PromptDetail.js
│   │   │   ├── ResearchJobDetail.js
│   │   │   └── UserProfile.js
│   │   ├── hooks               # Custom hooks if used (e.g. useAuth, usePromptData)
│   │   ├── store               # (Optional) Redux or Zustand store if used
│   │   ├── routes.js           # React Router config
│   │   └── App.css             # Global styling
│   ├── package.json
│   ├── yarn.lock (or package-lock.json)
│   └── .env.example            # Frontend environment variables (API_URL, etc.)
├── logs                        # Directory for storing logs (MVP uses file-based logging)
│   ├── backend.log
│   └── celery.log
└── scripts
    └── init_db.sh             # Script to initialize DB or run migrations (if needed)

