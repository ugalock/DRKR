CREATE TABLE organizations (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,
    description     TEXT,
    created_at      TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    external_id     VARCHAR(255) UNIQUE, 
    -- for OAuth/OpenID connect, store the provider’s user ID
    username        VARCHAR(50) NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    display_name    VARCHAR(100),
    default_role    VARCHAR(50) DEFAULT 'user', 
    created_at      TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE organization_members (
    id                 SERIAL PRIMARY KEY,
    organization_id    INT NOT NULL REFERENCES organizations (id) ON DELETE CASCADE,
    user_id            INT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    role               VARCHAR(50) NOT NULL DEFAULT 'member', 
    -- e.g. 'member', 'admin', 'owner'
    created_at         TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    UNIQUE (organization_id, user_id)
);

-- Refresh Tokens / API Keys / OAuth tokens can be stored in
-- a separate table (or external system) if needed. For example:
CREATE TABLE api_keys (
    id                  SERIAL PRIMARY KEY,
    user_id             INT REFERENCES users (id) ON DELETE CASCADE,
    organization_id     INT REFERENCES organizations (id) ON DELETE CASCADE,
    token               VARCHAR(255) NOT NULL UNIQUE,
    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    expires_at          TIMESTAMP WITHOUT TIME ZONE,

    -- Check that exactly one of user_id or organization_id is non-NULL
    CONSTRAINT chk_api_key_owner
    CHECK (
      (user_id IS NOT NULL AND organization_id IS NULL)
      OR (user_id IS NULL AND organization_id IS NOT NULL)
    )
);

CREATE EXTENSION IF NOT EXISTS vector;

-- The "main" table storing each deep-research record
CREATE TABLE deep_research (
    id                  SERIAL PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES users (id) ON DELETE SET NULL,
    owner_user_id       INT REFERENCES users (id) ON DELETE SET NULL,
    owner_org_id        INT REFERENCES organizations (id) ON DELETE SET NULL,
    visibility          ENUM ('private', 'public', 'org') NOT NULL DEFAULT 'public',
    title               VARCHAR(255) NOT NULL,
    prompt_text         TEXT NOT NULL,    -- The query or prompt
    final_report        TEXT NOT NULL,    -- The resulting "deep research" (could be very large)
    -- Alternatively, final_report can be stored as TEXT or 
    -- stored externally (S3, etc.) with a URL reference here. 
    prompt_tsv          tsvector,
    report_tsv          tsvector,
    prompt_embedding    vector(3072),
    report_embedding    vector(3072),
    model_name          VARCHAR(100),     -- e.g., GPT-4, LLaMA, etc.
    model_params        JSONB,            -- optional: store hyperparams or any additional LLM config
    source_count        INT DEFAULT 0,    -- number of sources/citations
    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- Optionally, track each chunk (section) of the final report 
-- for granular retrieval. 
CREATE TABLE research_chunks (
    id                  SERIAL PRIMARY KEY,
    deep_research_id    INT NOT NULL REFERENCES deep_research (id) ON DELETE CASCADE,
    chunk_index         INT NOT NULL,           -- ordering of the chunk
    chunk_type          VARCHAR(50),            -- e.g. "introduction", "analysis", "conclusion", etc.
    chunk_text          TEXT NOT NULL,          -- the text for this chunk
    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE research_summaries (
    id                  SERIAL PRIMARY KEY,
    deep_research_id    INT NOT NULL REFERENCES deep_research (id) ON DELETE CASCADE,
    summary_scope       VARCHAR(50) NOT NULL, 
    -- e.g. "report" or "prompt" (which text is being summarized)
    summary_length      VARCHAR(50) NOT NULL, 
    -- e.g. "2_pages", "1_page", "250_words", 
    -- or some numeric code like "long", "medium", "short"
    summary_text        TEXT NOT NULL,   -- the actual summary
    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- Example usage:
-- row1: summary_scope='report', summary_length='2_pages', summary_text='...'
-- row2: summary_scope='report', summary_length='1_page', summary_text='...'
-- row3: summary_scope='prompt', summary_length='250_words', summary_text='...'


CREATE TABLE research_sources (
    id                  SERIAL PRIMARY KEY,
    deep_research_id    INT NOT NULL REFERENCES deep_research (id) ON DELETE CASCADE,
    source_url          TEXT NOT NULL,
    source_title        TEXT,    
    source_excerpt      TEXT,
    domain             VARCHAR(255),   -- e.g. "nytimes.com", "arxiv.org", extracted from URL
    source_type        VARCHAR(50),    -- e.g. "website", "paper", "book", "pdf"
    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE domain_co_occurrences (
    id                  SERIAL PRIMARY KEY,
    domain_a            VARCHAR(255) NOT NULL,
    domain_b            VARCHAR(255) NOT NULL,
    co_occurrence_count  INT NOT NULL DEFAULT 0,
    last_updated        TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    UNIQUE(domain_a, domain_b)
);

CREATE TABLE tags (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(100) NOT NULL,  -- The tag label
    description         TEXT,
    is_global           BOOLEAN NOT NULL DEFAULT FALSE,
    organization_id     INT REFERENCES organizations (id) ON DELETE CASCADE,
    user_id             INT REFERENCES users (id) ON DELETE CASCADE,
    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
    -- You can add "updated_at" if you need it
);

/*
We want to ensure that a tag is either:
  - Global (is_global = true) and BOTH org_id and user_id are NULL
  - Org-specific (org_id not null) and is_global = false, user_id = NULL
  - User-specific (user_id not null) and is_global = false, org_id = NULL
*/

ALTER TABLE tags
ADD CONSTRAINT chk_tags_scope 
CHECK (
  (
    is_global = TRUE 
    AND organization_id IS NULL 
    AND user_id IS NULL
  )
  OR
  (
    is_global = FALSE
    AND organization_id IS NOT NULL 
    AND user_id IS NULL
  )
  OR
  (
    is_global = FALSE
    AND user_id IS NOT NULL
    AND organization_id IS NULL
  )
);

/*
For uniqueness, we don't want two tags with the same name
in the same scope (global, org, or user).
We can use partial unique indexes:
*/

-- 1) Unique name for GLOBAL tags:
CREATE UNIQUE INDEX unique_global_tag_name 
  ON tags (LOWER(name))
  WHERE is_global = TRUE;

-- 2) Unique name within each organization:
CREATE UNIQUE INDEX unique_org_tag_name
  ON tags (organization_id, LOWER(name))
  WHERE organization_id IS NOT NULL;

-- 3) Unique name within each user’s scope:
CREATE UNIQUE INDEX unique_user_tag_name
  ON tags (user_id, LOWER(name))
  WHERE user_id IS NOT NULL;

CREATE TABLE deep_research_tags (
    deep_research_id    INT NOT NULL REFERENCES deep_research (id) ON DELETE CASCADE,
    tag_id              INT NOT NULL REFERENCES tags (id) ON DELETE CASCADE,
    PRIMARY KEY (deep_research_id, tag_id)
);

CREATE TABLE research_ratings (
    id                  SERIAL PRIMARY KEY,
    deep_research_id    INT NOT NULL REFERENCES deep_research (id) ON DELETE CASCADE,
    user_id             INT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    rating_value        SMALLINT NOT NULL,  -- e.g., 1-5 rating or upvote/downvote
    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    -- If you want only one rating per user per research, 
    -- you can add a unique constraint:
    UNIQUE (deep_research_id, user_id)
);

CREATE TABLE research_comments (
    id                  SERIAL PRIMARY KEY,
    deep_research_id    INT NOT NULL REFERENCES deep_research (id) ON DELETE CASCADE,
    user_id             INT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    parent_comment_id   INT,   -- for nested threads
    comment_text        TEXT NOT NULL,
    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE research_auto_metadata (
    id                  SERIAL PRIMARY KEY,
    deep_research_id    INT NOT NULL REFERENCES deep_research (id) ON DELETE CASCADE,
    meta_key            VARCHAR(100) NOT NULL,   -- e.g., "keyword", "category", ...
    meta_value          TEXT NOT NULL,           -- e.g., "Machine Learning"
    confidence_score    FLOAT,                   -- optional
    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- ALTER TABLE deep_research
--     ADD COLUMN prompt_tsv tsvector,     -- for full-text indexing on the prompt 
--     ADD COLUMN report_tsv tsvector;     -- for full-text indexing on the final report


-- ALTER TABLE deep_research
--     ADD COLUMN prompt_embedding vector(3072),    -- example dimension
--     ADD COLUMN report_embedding vector(3072);
