# PostgreSQL + pgvector as primary database

We use a single PostgreSQL instance with the pgvector extension for all data — relational user profiles, recipe metadata, and vector embeddings for similarity search. No separate vector database.

PostgreSQL handles the relational workload well (user accounts, pantry junctions, interaction history), and pgvector adds approximate nearest-neighbor search on top of the same connection pool and backup strategy. For a solo project at this scale (tens of thousands of recipes, not billions), a dedicated vector DB like Pinecone or Weaviate would add operational overhead — a second service to deploy, monitor, and pay for — without a meaningful performance gain. pgvector's HNSW index is fast enough for recipe-scale similarity queries.

The hybrid recommendation pipeline (TF-IDF cosine similarity + collaborative filtering reranking) runs as a batch job that writes pre-computed vectors into a `VECTOR` column on the `recipes` table. At query time, the pantry match is a single `SELECT ... ORDER BY embedding <=> $1 LIMIT N` — no cross-service calls.

## Considered Options

- **pgvector**: Single database, vector search via extension, familiar tooling. Trade-off: slower than dedicated vector DBs at extreme scale (100M+ vectors), but irrelevant at this project's size.
- **Pinecone / Weaviate / Milvus**: Purpose-built vector DBs with better ANN performance. Trade-off: separate infrastructure, separate billing, separate failure modes — overkill for <100K recipe vectors.
- **SQLite + sqlite-vss**: Simpler deployment, no Postgres dependency. Trade-off: no concurrent writes, no full-text search, harder to add a REST API later.

## Consequences

- All data lives in one place — backups, migrations, and local dev are one `docker-compose up` away.
- If vector search becomes a bottleneck (unlikely at this scale), the migration path is to extract embeddings into a dedicated service — the `VECTOR` column is the only thing that changes.
- The import script, API server, and ML training pipeline all share the same connection string and schema, which simplifies the codebase significantly.
