# Global Search POC — Semantic Search & Visual Analytics

A Proof-of-Concept (POC) for RecVue's Global Search architecture, now featuring:
- **Oracle DB integration** (migrated from H2)
- **Delta Refresh logic** for change tracking
- **Embedding Generation** using sentence-transformers
- **ChromaDB** for vector-based semantic search
- **Multi-tenant support**
- **Modern Streamlit UI** with rich visual analytics

---

## 🏗️ Architecture Overview

- **Database Layer**: Oracle DB (or H2 for legacy/testing)
- **Delta Refresh Layer**: Extracts and processes new/changed records
- **Embedding Layer**: Generates vector embeddings for order data
- **Semantic Search Layer**: ChromaDB for fast, contextual search
- **Visual Analytics Layer**: Streamlit app for interactive, visual search

---

## 🚀 Features

- **Oracle Integration**: Reads and joins real Oracle tables for order, billing, delivery, and pricing data
- **Delta Refresh**: Efficiently processes only new/changed records
- **Semantic Search**: Uses vector embeddings for context-aware search (not just keywords)
- **Multi-Tenant**: Each tenant has a separate ChromaDB collection
- **Visual UI**: Streamlit dashboard with charts, progress bars, and insights
- **Test & Demo Scripts**: CLI tools for backfill, search, and analytics

---

## ⚡ Quick Start & Execution Steps

### 1. **Clone the Repository**
```bash
git clone <repo-url>
cd Global_Search_POC
```

### 2. **Set Up Python Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. **Configure Database**
- Update Oracle connection details in `config/db_config.py`.
- (Optional) For H2, download the JAR and update the path.

### 4. **Prepare Oracle Schema & Data**
- Ensure Oracle tables are created and populated (see `database/schema.sql` for reference).
- Place any required CSVs and run import scripts if needed.

### 5. **Backfill & Embedding Generation**
```bash
python backfill_orders.py  # Loads and embeds order data into ChromaDB
```

### 6. **Run the API Server**
```bash
python api/app.py  # Starts the Flask API for search and refresh
```

### 7. **Launch the Visual Search UI**
```bash
streamlit run streamlit_app.py
# Open http://localhost:8501 in your browser
```

### 8. **Try Semantic Search**
- Use the Streamlit UI for interactive search and analytics
- Or test via CLI:
```bash
python test_search.py
python demo_search.py
python test_visual_search.py
```

---

## 📊 Visual Analytics & Insights
- **Score Distribution**: Histogram of semantic match scores
- **Status Pie Chart**: Order status breakdown
- **Relevance Progress Bars**: Color-coded for easy interpretation
- **AI Insights**: Query quality, result diversity, and business context
- **Expandable Details**: See full record info for each result

---

## 🛠️ Key Files
- `api/app.py` — Flask API for search, insert, and refresh
- `streamlit_app.py` — Visual UI for semantic search and analytics
- `backfill_orders.py` — Loads and embeds data from Oracle
- `delta_refresh/tenant_pipeline.py` — Delta refresh logic
- `utils/embedding_generator.py` — Embedding model
- `chroma_module/` — ChromaDB integration
- `test_search.py`, `demo_search.py`, `test_visual_search.py` — CLI test/demo scripts

---

## 📝 Notes
- **Dependencies**: See `requirements.txt` (Flask, Streamlit, sentence-transformers, chromadb, plotly, pandas, oracledb, etc.)
- **Oracle DB**: Ensure network access and credentials are correct
- **ChromaDB**: Uses local persistent storage in `chroma_storage/`
- **Multi-Tenant**: Switch tenants in the Streamlit sidebar

---
**Author:** Rohit Menon
