# Global Search Layer 1 POC Architecture

## 1. System Overview

- **Mock Oracle DB**: Implemented using H2 with an Oracle-compatible schema.
- **Delta Refresh Engine**: Tracks changes via the `change_log` table and processes new rows.
- **Prompt Validation**: `utils/prompt_validator.py` filters irrelevant prompts before embeddings are generated.
- **Embedding Generation**: `utils/embedding_generator.py` uses `sentence-transformers` to create vector embeddings.
- **Multi-tenant ChromaDB**: `chromadb/multitenant_chroma.py` manages per-tenant collections for semantic search.
- **Scheduled Jobs**: `delta_refresh/scheduler.py` runs the tenant refresh pipeline on a timer.

## 2. Directory Structure

```text
.
├── chromadb/
│   ├── chroma_client.py
│   ├── chroma_query.py
│   ├── chroma_updater.py
│   └── multitenant_chroma.py
├── config/
│   └── db_config.py
├── database/
│   └── schema.sql
├── delta_refresh/
│   ├── delta_engine.py
│   ├── pipeline.py
│   ├── scheduler.py
│   └── tenant_pipeline.py
├── delta_refresh_engine/
│   ├── __init__.py
│   └── delta_refresh_engine.py
├── evaluation/
│   └── model_metrics.md
├── layer1/
│   ├── db_connection.py
│   ├── db_sanity_check.py
│   ├── delta_extractor.py
│   ├── extractor.py
│   ├── inserter.py
│   ├── layer1_inserter.py
│   ├── oracle_adapter.py
│   └── sanity_check.py
├── utils/
│   ├── embedding_generator.py
│   └── prompt_validator.py
└── requirements.txt
```

## 3. Module Responsibilities

- **database/schema.sql**: Initializes the H2 tables used by the POC.
- **config/db_config.py**: Stores JDBC URL, credentials, and H2 JAR path.
- **layer1/db_connection.py**: Helper to create H2 connections.
- **layer1/inserter.py**: Inserts orders and logs them in `change_log`.
- **layer1/extractor.py**: Reads delta changes from `change_log`.
- **layer1/sanity_check.py**: Performs a basic DB health check.
- **delta_refresh/delta_engine.py**: Processes deltas from `change_log`.
- **delta_refresh/tenant_pipeline.py**: Multi-tenant refresh logic with per-tenant collections.
- **delta_refresh/pipeline.py**: Simple non-tenant refresh pipeline.
- **delta_refresh/scheduler.py**: Runs the tenant pipeline on a schedule.
- **utils/embedding_generator.py**: Generates embeddings using sentence-transformers.
- **utils/prompt_validator.py**: Filters prompts for business-domain relevance.
- **chromadb/chroma_client.py**: Connects to a ChromaDB instance.
- **chromadb/multitenant_chroma.py**: Manages tenant-specific collections.
- **chromadb/chroma_query.py**: Provides semantic search interface.
- **layer1/oracle_adapter.py**: Scaffold for Oracle production integration.

## 4. Deployment Notes

1. Update the H2 JAR path in `config/db_config.py` to match your environment.
2. Install all dependencies via `requirements.txt`.
3. Execute `database/schema.sql` in the H2 console before running any pipelines.
4. Future Oracle integration will use `layer1/oracle_adapter.py` for live connections.

## 5. Future Enhancements

- Live Oracle change data capture (CDC) integration.
- Retrieval Augmented Generation (RAG) for enriched search responses.
- Serverless deployment for the scheduler component.
- UI layer to allow users to run semantic search queries.
