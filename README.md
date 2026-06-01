High Level Architecture:

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