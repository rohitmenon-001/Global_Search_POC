# Global Search POC — Layer 1 Architecture

A POC implementation of Layer 1 for RecVue's Global Search architecture using H2 (Oracle mock), Delta Refresh logic, Embedding Generation, and ChromaDB semantic search.

## Architecture Overview

- **Database Layer**: H2 Oracle-compatible mock
- **Delta Refresh Layer**: change log extraction
- **Embedding Layer**: sentence-transformers
- **Semantic Search Layer**: ChromaDB integration

## Setup Instructions

1. Clone repo
2. Install requirements via `pip install -r requirements.txt`
3. Download the H2 jar file and update the path in `config/db_config.py`
4. Create the schema by executing `database/schema.sql` inside the H2 console
5. Start inserting data (`layer1/inserter.py`)
6. Run the delta refresh pipeline (`delta_refresh/pipeline.py`)
7. Perform semantic search (`chromadb/chroma_query.py`)

## Future Enhancements

- Full Oracle CDC integration
- Production-scale embedding pipelines
- Multi-tenant ChromaDB design

---
**Author:** Rohit Menon
