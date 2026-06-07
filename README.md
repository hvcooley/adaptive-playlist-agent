High Level Architecture:

-------------------
Data Ingestion
-------------------
Spotify API
    |
    v
Ingestion Pipeline
    |
    +--> PostgreSQL
    |
    +--> Embedding Generation
              |
              v
          Pinecone


--------------------
Agent Flow
--------------------
User Query
    |
    v
Planner Agent
    |
    +--> Query Expansion
    |
    +--> Artist Retrieval (Vector DB)
    |
    +--> Artist Ranking
    |
    +--> Song Retrieval
    |
    +--> Playlist Generation
    |
    +--> Critique Agent
             |
             +--> Retry?
                    |
                    +--> Refine Retrieval
                    +--> Generate Again



## Setup

1. Copy .env.example to .env

```bash
cp .env.example .env