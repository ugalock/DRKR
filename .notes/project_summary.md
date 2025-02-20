# Comprehensive Project Summary

Below is a **comprehensive project summary** that consolidates all major functionalities and design features. This summary is intended to give a future Large Language Model (or developer) a **complete understanding** of the platform’s vision, core data entities, and how everything fits together.

---

## 1. Core Concept

This platform is a structured **knowledge repository** for storing the outputs of “deep research.” A *deep research* instance typically contains:

1. **Prompt/Query** – The original question or topic being explored, along with metadata (user, date, tags, domain, etc.).  
2. **Final Report** – A detailed, well-structured analysis of the topic, including references, explanations, and expansions.  
3. **Metadata** – Automatic or user-supplied tags, timestamps, ratings, or additional data (e.g. LLM model used, user roles, organization ownership).  
4. **Vector Embeddings** – For both the prompt and the final report (often chunked), enabling semantic search and RAG (Retrieval-Augmented Generation).  
5. **Summaries** – Multiple summaries of various lengths (e.g., 2-page, 1-page, 250-word) for quick scanning or deeper reading.

Over time, the repository becomes a **living library** of curated research items, accessible via a **web front-end** or an **API**, with community engagement, version tracking, private/public scoping, and advanced retrieval features.

---

## 2. Major Features & Goals

### 2.1 Retrieval-Augmented Generation (RAG)

- **Semantic Search**: The platform stores embeddings in a vector database (Pinecone). Future AI queries can find and re-use relevant chunks from past research, boosting accuracy and reducing redundant queries.  
- **Source Integration**: Each research entry cites external sources. Those can be merged into new responses, building on verified references.

### 2.2 Collaboration & Community

- **User & Organization Scopes**: Research can be “private” (owned by one user), “org” (shared among members of an organization), or “public” (visible to everyone).  
- **Crowdsourced Knowledge**: Users can rate research, comment on them, or tag them with relevant metadata. Over time, a collective intelligence emerges.  
- **Advanced Tagging**: Tags can be global, organization-specific, or even user-specific, preventing naming conflicts or duplication.  
- **Moderation & Validation**: Moderators can confirm the correctness of research items, apply official tags, or promote high-quality content.  
- **Subreddit-like Tag Channels**: The system can host “sub-reddits” organized by **pre-approved tags**, where people can view Prompt:Report + metadata “posts.” Moderators (or tag owners) can help validate entries within these channels, ensuring quality and relevance.

### 2.3 Multi-Length Summaries

- **Various Summaries**: Each prompt or report can have multiple pre-generated summaries of different lengths (e.g., 2 pages, 1 page, 250 words).  
- **Chunking**: The final research can also be chunked into subsections (introduction, analysis, conclusion, etc.)—each chunk can be embedded separately for granular retrieval.

### 2.4 Graph-Building & Domain Analysis

- **Sources Table**: Tracks every external link or reference used in a final report. By parsing domains, the system can build a **co-occurrence graph** to show which sites or papers appear together often.  
- **Ratings & Moderation**: Only positively rated or moderator-verified research might be included in certain “official” domain graphs, ensuring quality control.

---

## 3. Data Model Overview

### 3.1 PostgreSQL (Relational)

The **relational database** handles user management, organizations, the main deep-research records, summaries, and all associated metadata. Key tables include:

1. **Users**  
   - Stores user info (e.g., `username`, `email`, `external_id` for OAuth).  

2. **Organizations**  
   - Represents a business, team, or any group context.  

3. **Organization_Members**  
   - Links a user to an org with a specific role (e.g., `member`, `admin`).  

4. **Deep_Research**  
   - The primary table capturing each “deep research” item: prompt text, final report, model info, timestamps, ownership (user or org), and visibility (`private`, `org`, or `public`).  

5. **Research_Summaries**  
   - Stores multiple summaries of each deep-research item at varying lengths (`2_pages`, `1_page`, `250_words`, etc.), or for both prompt and final report.  

6. **Research_Chunks** (optional)  
   - Breaks a final report into smaller sections. Each chunk can be embedded for more granular RAG searches.  

7. **Research_Sources**  
   - Tracks references or links cited in the report. Includes fields such as `source_url`, `domain`, and `source_excerpt`. This enables domain-level analysis and graph-building.  

8. **Tags**  
   - Supports **global tags**, **organization-specific tags**, and **user-specific tags**.  
   - A check constraint enforces that each tag is strictly one of these three types.  
   - Partial unique indexes prevent duplicate tag names in the same scope.  

9. **Deep_Research_Tags** (join table)  
   - Many-to-many link between a deep-research record and tags.  

10. **Research_Ratings**  
    - Records user ratings (e.g., 1–5 or up/downvote).  

11. **Research_Comments**  
    - Allows discussion threads on each deep-research item.  

12. **Research_Auto_Metadata** (optional)  
    - A flexible key-value table for automatically generated metadata (like extracted keywords, named entities).  

13. **API_Keys**  
    - Each row has either a `user_id` or an `organization_id` via a constraint, allowing keys for personal use or entire org use.  

### 3.2 Pinecone (Vector Database)

Used for **semantic similarity** and quick embedding-based retrieval:

- **Single Index** (commonly)  
  - Each entry has a unique `id` (e.g. `research:{deep_research_id}:chunk:{chunk_index}`).  
  - A `values` array containing the embedding (dimension ~768, 1024, 1536, etc., depending on the model).  
  - **Metadata**: `deep_research_id`, `chunk_type` (e.g., “prompt”, “report_chunk”, “summary”), `visibility`, `owner_org_id`, `tags`, `domain`, etc.  
- **Filtering**: By metadata like “visibility = public” or “type = prompt_summary” to refine search results.  
- This setup supports RAG workflows where queries are first embedded, then matched against prior research or summaries.

---

## 4. RBAC & Visibility

1. **Private**: Only the record’s owner user can access.  
2. **Org**: Any member of the same organization can read or modify.  
3. **Public**: Visible system-wide.  
4. **Roles**: In an organization, a user can be `member`, `admin`, `owner`, etc. Future expansions may allow fine-grained permissions (like who can rate vs. who can delete).  
5. **API Keys**: Tied to either a user or an organization, enabling external integrations (e.g., third-party research agents pushing new data or retrieving existing knowledge).

---

## 5. Use Cases & Flow

1. **Users or Bots Upload Research**  
   - They provide a prompt, final report, sources, tags, and possibly multiple summaries.  
   - The system saves these in Postgres; any chunking or embedding is done in a background task.  
   - The embeddings are pushed to Pinecone, allowing future semantic search.

2. **Search & Retrieval**  
   - A new query arrives. The system embeds that query and calls Pinecone to find top-matching chunks or summaries.  
   - The user sees relevant references from prior deep-research items—particularly helpful for RAG.

3. **Graph of Frequently Used Sources**  
   - By analyzing all `research_sources` with good ratings, the system can discover recurring domains or references.  
   - Over time, you can build a “network map” of how certain websites and references interconnect across tags or topics.

4. **Summaries at Different Granularities**  
   - The repository can store multiple *length-based* or *scope-based* summaries. For instance, a quick 250-word version or a more in-depth 2-page summary.  
   - This allows future LLM prompts or readers to decide how in-depth they want the content.

5. **Collaboration & Community**  
   - Members of an organization can share private knowledge internally without exposing it publicly.  
   - Public items can be rated by all. Comments and discussions can refine quality, highlight mistakes, or add clarifications.  
   - “Sub-reddit” style tag channels let people browse research items grouped by pre-approved tags, with moderator validation and ongoing improvements.

---

## 6. Long-Term Vision

1. **Extensible Knowledge Base**  
   - The platform becomes a go-to repository for thorough research on various domains.  
   - Integrations allow “deep research bots” to push new content or retrieve existing knowledge on the fly.

2. **Advanced RAG**  
   - As more “deep research” is stored, new LLM-based systems rely less on external web searches and more on curated internal data.  
   - This reduces hallucinations by referencing validated, rated, and curated materials.

3. **Community-Driven**  
   - Crowdsourced tagging and rating surfaces the best or most authoritative research.  
   - Over time, a social dimension (sub-channels, discussions, user reputation) could form a strong knowledge-sharing network.

4. **Graph Analysis**  
   - Tracking how sources or domains intersect across high-rated research fosters insights into domain relationships, influencer websites, or top-cited reference clusters.

5. **Rich RBAC & Multi-Tenancy**  
   - Fine-grained access controls for organizations.  
   - Private research for enterprise settings, with advanced IAM roles for large teams.  
   - Potential for marketplace or paid tiers to handle large-scale usage.

---

## 7. Conclusion

This project is a **versatile, multi-layer knowledge repository** aimed at storing, indexing, and rediscovering *deep research outputs*. The data model harnesses **PostgreSQL** for structured data and relationships (users, orgs, roles, tags, comments, sources) and **Pinecone** for powerful **vector-based** search. Additional features like **multi-length summaries**, **RBAC** with private/org/public scoping, **sub-reddit style channels**, and **source domain graph-building** place it at the forefront of a modern knowledge management system that is *AI-ready* for advanced retrieval and collaboration.
