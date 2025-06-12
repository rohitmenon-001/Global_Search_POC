# Global Search POC

This repository demonstrates a basic global search pipeline using a small H2
database. The code is organised as a set of lightweight modules that can be
expanded into a full search service. The key directories are shown below.

```
global-search-poc/
│
├── README.md
├── requirements.txt
├── h2_db/
│   ├── schema.sql            # DB table creation scripts
│   └── h2-2.x.x.jar          # H2 JDBC jar (local copy for reference)
│
├── layer1/
│   ├── __init__.py           # Package marker
│   ├── db_connection.py      # DB connection logic (reusable)
│   ├── layer1_inserter.py    # Insert + change log logic
│   ├── delta_extractor.py    # Extract deltas from change log
│   └── db_sanity_check.py    # Quick health check of DB
│
├── delta_refresh_engine/
│   ├── __init__.py
│   └── delta_refresh_engine.py  # Refresh loop skeleton
│
├── chromadb_integration/     # Future: code to feed ChromaDB
│   └── (future scripts)
│
└── utils/                    # Optional helpers
    └── (empty for now)
```

An additional `evaluation/` folder contains benchmarking documentation for
future reference.

To get started, install the required dependencies:

```bash
pip install -r requirements.txt
```

The modules are placeholders and do not yet provide a working application.
They are intended as a starting point for further development.
